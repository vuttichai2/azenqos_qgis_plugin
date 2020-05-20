from PyQt5.QtSql import QSqlQuery, QSqlDatabase


class WcdmaDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getActiveMonitoredSets(self):
        self.openConnection()
        dataList = []
        maxUnits = 27
        condition = ""
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        for unit in range(maxUnits):
            temp = []
            queryString = None
            unitNo = unit + 1
            elementDictList = [
                {
                    "element": "wcmc",
                    "table": "wcdma_cells_combined",
                    "column": (
                        "wcdma_cellfile_matched_cellname_%d,wcdma_celltype_%d,wcdma_sc_%d,wcdma_ecio_%d,wcdma_rscp_%d,wcdma_cellfreq_%d"
                        % (unitNo, unitNo, unitNo, unitNo, unitNo, unitNo)
                    ),
                    "join": {
                        "element": "wp",
                        "table": "wcdma_rrc_meas_events",
                        "column": "wcdma_prevmeasevent ",
                    },
                }
            ]

            for dic in elementDictList:
                element = dic["element"]
                mainColumn = dic["column"]
                subColumn = dic["column"]
                table = dic["table"]
                join = None
                joinString = ""
                onString = ""
                if dic["join"]:
                    join = dic["join"]
                    joinString = """JOIN ( SELECT %s,1 as row_num 
                                          FROM %s 
                                          %s 
                                          ORDER BY time DESC 
                                          LIMIT 1 
                                        ) %s """ % (
                        join["column"],
                        join["table"],
                        condition,
                        join["element"],
                    )
                    onString = """ON %s.row_num = %s.row_num""" % (
                        element,
                        join["element"],
                    )
                    mainColumn += ",%s" % join["column"]

                if element and mainColumn and table:
                    queryString = """SELECT %s
                                    FROM ( SELECT %s,1 as row_num
                                            FROM %s 
                                            %s 
                                            ORDER BY time DESC 
                                            LIMIT 1 
                                        ) %s 
                                    %s 
                                    %s 
                                    """ % (
                        mainColumn,
                        subColumn,
                        table,
                        condition,
                        element,
                        joinString,
                        onString,
                    )
                    query = QSqlQuery()

                    query.exec_(queryString)
                    if query.first():
                        for i in range(0, len(mainColumn.split(","))):
                            if str(query.value(i)) == "NULL":
                                temp.append("")
                            else:
                                temp.append(query.value(i))
            if not all(v == "" for v in temp):
                if len(dataList) == 0:
                    temp.insert(0, self.timeFilter)
                else:
                    temp.insert(0, "")
                dataList.append(temp)
        if len(dataList) == 0:
            dataList.append([self.timeFilter, "", "", "", "", "", "", ""])
        self.closeConnection()
        return dataList

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
            dataList.append(["Time", self.timeFilter, ""])

        elementDictList = [
            {
                "name": "wtp",
                "element": "Tx Power,Max Tx Power",
                "table": "wcdma_tx_power",
                "column": "wcdma_txagc,wcdma_maxtxpwr",
                "join": [
                    {
                        "name": "wrp",
                        "element": "RSSI",
                        "table": "wcdma_rx_power",
                        "column": "wcdma_rssi",
                    },
                    {
                        "name": "ws",
                        "element": "SIR",
                        "table": "wcdma_sir",
                        "column": "wcdma_sir",
                    },
                    {
                        "name": "wrs",
                        "element": "RRC State",
                        "table": "wcdma_rrc_state",
                        "column": "wcdma_rrc_state",
                    },
                    {
                        "name": "vi",
                        "element": "Speech Codec TX,Speech Codec RX",
                        "table": "vocoder_info",
                        "column": "gsm_speechcodectx,gsm_speechcodecrx",
                    },
                    {
                        "name": "ai",
                        "element": "Cell ID,RNC ID",
                        "table": "android_info_1sec",
                        "column": "android_cellid,android_rnc_id",
                    },
                ],
            }
        ]
        for dic in elementDictList:
            temp = []
            name = dic["name"]
            element = dic["element"]
            mainElement = dic["element"]
            mainColumn = dic["column"]
            subColumn = dic["column"]
            table = dic["table"]
            join = None
            joinString = ""
            onString = ""
            if not len(dic["join"]) == 0:
                for join in dic["join"]:
                    onString = """ON %s.row_num = %s.row_num""" % (name, join["name"],)
                    joinString += """LEFT JOIN ( SELECT %s,1 as row_num 
                                            FROM %s 
                                            %s 
                                            ORDER BY time DESC 
                                            LIMIT 1 
                                        ) %s
                                        %s """ % (
                        join["column"],
                        join["table"],
                        condition,
                        join["name"],
                        onString,
                    )

                    mainColumn += ",%s" % join["column"]
                    mainElement += ",%s" % join["element"]

            if element and mainColumn and table:
                queryString = """SELECT %s
                                FROM ( SELECT %s,1 as row_num
                                        FROM %s 
                                        %s 
                                        ORDER BY time DESC 
                                        LIMIT 1 
                                    ) %s
                                %s 
                                """ % (
                    mainColumn,
                    subColumn,
                    table,
                    condition,
                    name,
                    joinString,
                )
                query = QSqlQuery()
                query.exec_(queryString)
                elements = mainElement.split(",")
                if query.first():
                    for i in range(0, len(elements)):
                        temp.append(
                            [
                                elements[i],
                                "" if str(query.value(i)) == "NULL" else query.value(i),
                                "",
                            ]
                        )
                else:
                    for elem in elements:
                        temp.append([elem, "", ""])
            dataList.extend(temp)
        self.closeConnection()
        return dataList

    def getActiveSetList(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxUnits = 3
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        for unit in range(maxUnits):
            temp = []
            queryString = None
            unitNo = unit + 1
            # selectedColumns = (
            #     "wcc.wcdma_cellfile_matched_cellname_%d, wcc.wcdma_celltype_%d, wcc.wcdma_sc_%d, wcc.wcdma_ecio_%d, wcc.wcdma_rscp_%d, wcc.wcdma_cellfreq_%d, wcc.wcdma_cellfreq_%d"
            #     % (unitNo, unitNo, unitNo, unitNo, unitNo, unitNo, unitNo)
            # )
            elementDictList = [
                {
                    "element": "wcm",
                    "table": "wcdma_cell_meas",
                    "column": ("wcdma_aset_cellfreq_%d" % unitNo),
                    "join": {
                        "element": "wafl",
                        "table": "wcdma_aset_full_list",
                        "column": "wcdma_activeset_psc_%d,wcdma_activeset_cellposition_%d,wcdma_activeset_celltpc_%d,wcdma_activeset_diversity_%d"
                        % (unitNo, unitNo, unitNo, unitNo),
                    },
                }
            ]

            for dic in elementDictList:
                element = dic["element"]
                mainColumn = dic["column"]
                subColumn = dic["column"]
                table = dic["table"]
                join = None
                joinString = ""
                onString = ""
                if dic["join"]:
                    join = dic["join"]
                    joinString = """JOIN ( SELECT %s,1 as row_num 
                                          FROM %s 
                                          %s 
                                          ORDER BY time DESC 
                                          LIMIT 1 
                                        ) %s """ % (
                        join["column"],
                        join["table"],
                        condition,
                        join["element"],
                    )
                    onString = """ON %s.row_num = %s.row_num""" % (
                        element,
                        join["element"],
                    )
                    mainColumn += ",%s" % join["column"]

                if element and mainColumn and table:
                    queryString = """SELECT %s
                                    FROM ( SELECT %s,1 as row_num
                                            FROM %s 
                                            %s 
                                            ORDER BY time DESC 
                                            LIMIT 1 
                                        ) %s 
                                    %s 
                                    %s 
                                    """ % (
                        mainColumn,
                        subColumn,
                        table,
                        condition,
                        element,
                        joinString,
                        onString,
                    )
                    query = QSqlQuery()

                    query.exec_(queryString)
                    if query.first():
                        for i in range(0, len(mainColumn.split(","))):
                            if str(query.value(i)) == "NULL":
                                temp.append("")
                            else:
                                temp.append(query.value(i))

            if not all(v == "" for v in temp):
                if len(dataList) == 0:
                    temp.insert(0, self.timeFilter)
                else:
                    temp.insert(0, "")
                dataList.append(temp)
        if len(dataList) == 0:
            dataList.append([self.timeFilter, "", "", "", "", "", "", ""])
        self.closeConnection()
        return dataList

    def getMonitoredSetList(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxUnits = 32
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        for unit in range(maxUnits):
            unitNo = unit + 1
            selectedColumns = (
                """time,wcdma_neighborset_downlinkfreq_%d,wcdma_neighborset_psc_%d,wcdma_neighborset_cellposition_%d,wcdma_neighborset_diversity_%d"""
                % (unitNo, unitNo, unitNo, unitNo)
            )
            queryString = (
                """SELECT %s FROM wcdma_nset_full_list %s ORDER BY time DESC LIMIT 1"""
                % (selectedColumns, condition,)
            )
            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                freqValue = "" if str(query.value(1)) == "NULL" else query.value(1)
                pscValue = "" if str(query.value(2)) == "NULL" else query.value(2)
                celposValue = "" if str(query.value(3)) == "NULL" else query.value(3)
                diverValue = "" if str(query.value(4)) == "NULL" else query.value(4)
                if unitNo == 1:
                    dataList.append(
                        [self.timeFilter, freqValue, pscValue, celposValue, diverValue]
                    )
                else:
                    if not all(
                        str(v) == ""
                        for v in [freqValue, pscValue, celposValue, diverValue]
                    ):
                        dataList.append(
                            ["", freqValue, pscValue, celposValue, diverValue]
                        )
            else:
                if len(dataList) == 0:
                    dataList.append([self.timeFilter, "", "", "", "", ""])

        self.closeConnection()
        return dataList

    def getBlerSummary(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            "Time",
            "BLER Average Percent",
            "BLER Calculation Window Size",
            "BLER N Transport Channels",
        ]
        condition = ""
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        queryString = """Select time,wcdma_bler_average_percent_all_channels,wcdma_bler_calculation_window_size,
                        wcdma_bler_n_transport_channels
                        FROM wcdma_bler
                        %s
                        ORDER BY time DESC LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            dataList.append(["Time", self.timeFilter])
            blerAvg = query.value(1)
            blerCalWindowSize = query.value(2)
            blerNTransportChannels = query.value(3)
            for field in range(1, len(fieldsList)):
                dataList.append(
                    [
                        fieldsList[field],
                        "" if str(query.value(field)) == "NULL" else query.value(field),
                    ]
                )
        else:
            if len(dataList) == 0:
                dataList.append(["Time", self.timeFilter])
                for field in range(1, len(fieldsList)):
                    dataList.append([fieldsList[field], ""])
        self.closeConnection()
        return dataList

    def getBLER_TransportChannel(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxChannel = 16

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        for channel in range(maxChannel):
            channelNo = channel + 1
            queryString = """SELECT wcdma_bler_channel_%d,wcdma_bler_percent_%d,
                            wcdma_bler_err_%d,wcdma_bler_rcvd_%d
                            FROM wcdma_bler
                            %s
                            ORDER BY time DESC LIMIT 1""" % (
                channelNo,
                channelNo,
                channelNo,
                channelNo,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                row = []
                for i in range(4):
                    row.append("" if str(query.value(i)) == "NULL" else query.value(i))
                if not all(str(v) == "" for v in row):
                    dataList.append(row)
            else:
                if len(dataList) == 0:
                    dataList.append(["", "", "", ""])

        self.closeConnection()
        return dataList

    def getBearers(self):
        self.openConnection()
        dataList = []
        condition = ""
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        maxBearers = 10
        for bearers in range(1, maxBearers):
            bearerNo = bearers + 1
            queryString = """SELECT data_wcdma_n_bearers,data_wcdma_bearer_id_%d,data_wcdma_bearer_rate_dl_%d,
                             data_wcdma_bearer_rate_ul_%d
                             FROM wcdma_bearers %s
                             ORDER BY time DESC LIMIT 1""" % (
                bearerNo,
                bearerNo,
                bearerNo,
                condition,
            )

            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                row = ["", "", "", ""]
                if bearerNo == 1:
                    row[0] = query.value(0)
                for index in range(1, len(row)):
                    row[index] = (
                        "" if str(query.value(index)) == "NULL" else query.value(index)
                    )
                if not all(str(v) == "" for v in row):
                    dataList.append(row)
            else:
                if len(dataList) == 0:
                    dataList.append(["", "", "", ""])
        self.closeConnection()
        return dataList

    def getPilotPolutingCells(self):
        self.openConnection()
        dataList = []
        condition = ""
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        maxPollution = 32
        for pollution in range(maxPollution):
            pollutionNo = pollution + 1
            queryString = """SELECT time,wcdma_n_pilot_polluting_cells,wcdma_pilot_polluting_cell_sc_%d,
                             wcdma_pilot_polluting_cell_rscp_%d,wcdma_pilot_polluting_cell_ecio_%d
                             FROM wcdma_pilot_pollution
                             %s
                             ORDER BY time DESC LIMIT 1""" % (
                pollution,
                pollution,
                pollution,
                condition,
            )

            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                row = ["", "", "", "", ""]
                if pollutionNo == 1:
                    row[0] = "" if str(query.value(0)) == "NULL" else query.value(0)
                    row[1] = "" if str(query.value(1)) == "NULL" else query.value(1)
                for index in range(2, len(row)):
                    row[index] = (
                        "" if str(query.value(index)) == "NULL" else query.value(index)
                    )
                if not all(str(v) == "" for v in row):
                    dataList.append(row)

        self.closeConnection()
        return dataList

    def getActiveMonitoredBar(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxItem = 27

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        for item in range(maxItem):
            itemNo = item + 1
            queryString = """SELECT wcdma_celltype_%d,wcdma_ecio_%d,wcdma_rscp_%d
                            FROM wcdma_cells_combined
                            %s
                            ORDER BY time DESC""" % (
                itemNo,
                itemNo,
                itemNo,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                row = []
                for i in range(3):
                    row.append("" if str(query.value(i)) == "NULL" else query.value(i))
                if not all(str(v) == "" for v in row):
                    dataList.append(row)
            else:
                if len(dataList) == 0:
                    dataList.append(["", "", ""])

        self.closeConnection()
        return dataList

    def getCmGsmCells(self):
        self.openConnection()
        dataList = []
        condition = ""

        queryString = """Select time,wcdma_cm_gsm_meas_arfcn,wcdma_cm_gsm_meas_rxlev,
                        wcdma_cm_gsm_meas_bsic,wcdma_cm_gsm_meas_cell_measure_state
                        FROM wcdma_cm_gsm_meas
                        %s
                        ORDER BY time DESC LIMIT 1""" % (
            condition
        )

        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            row = []
            for i in range(5):
                row.append("" if str(query.value(i)) == "NULL" else query.value(i))
            if not all(str(v) == "" for v in row):
                dataList.append(row)
        else:
            dataList.append([self.timeFilter, "", "", "", ""])
        self.closeConnection()
        return dataList

    def openConnection(self):
        if self.azenqosDatabase is not None:
            self.azenqosDatabase.open()

    def closeConnection(self):
        self.azenqosDatabase.close()

    def defaultData(self, fieldsList):
        fieldCount = len(fieldsList)
        if fieldCount > 0:
            dataList = []
            for index in range(fieldCount):
                columnName = fieldsList[index]
                value = ""
                dataList.append([columnName, value, "", ""])
            return dataList
