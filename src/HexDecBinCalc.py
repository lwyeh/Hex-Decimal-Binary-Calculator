import wx
import wx.grid as gridlib
import wx.html
import wx.lib.mixins.gridlabelrenderer as glr
import string

COLOR_LIST = (wx.WHITE, wx.CYAN)
LABEL_COLOR_LIST = ('#C0C0C0', '#3299CC')
MAX_BIT_NUM = 32 # 64
UNIT_NUM = 4
MERGE_ROW_NUM = 1
MERGE_COL_NUM = UNIT_NUM
MODE_STATUS_STR = ("Mode: one calculator mode", "Mode: two calculator mode (for comparison two binary value)")
HEX_LENGTH = 8 # 16
ST_HEX_LENGTH = (HEX_LENGTH + 2)
ST_DEC_LENGTH = 10 # 20

WIN_SIZE_X = 680 # 1350
WIN_SIZE_Y = 260

HEX_DIGIT_ONLY = 1
DIGIT_ONLY = 2
EXP_CHR_ONLY = 3
ALL_CHAR_NOT = 4

MAX_NUM = 0xFFFFFFFF # 0xFFFFFFFFFFFFFFFF
strExpChr = string.hexdigits + "xX+-*/&|^()<>% "

VERSION = "v1.4"

class MyValidator(wx.PyValidator):
    def __init__(self, flag=None, pyVar=None):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return MyValidator(self.flag)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        if self.flag == HEX_DIGIT_ONLY:
            for x in val:
                if x not in string.hexdigits:
                    return False
        elif self.flag == DIGIT_ONLY:
            for x in val:
                if x not in string.digits:
                    return False
        elif self.flag == EXP_CHR_ONLY:
            for x in val:
                if x not in strExpChr:
                    return False
        elif self.flag == ALL_CHAR_NOT:
            return False
        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return
        if self.flag == HEX_DIGIT_ONLY and chr(key) in string.hexdigits:
            event.Skip()
            return
        if self.flag == DIGIT_ONLY and chr(key) in string.digits:
            event.Skip()
            return
        if self.flag == EXP_CHR_ONLY and chr(key) in strExpChr:
            event.Skip()
            return
        if self.flag == ALL_CHAR_NOT:
            wx.Bell()
            return
        if not wx.Validator_IsSilent():
            wx.Bell()
        # Returning without calling event.Skip eats the event before it
        # gets to the text control
        return

class MyColLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor):
        self._bgcolor = bgcolor

    def Draw(self, grid, dc, rect, col):
        dc.SetBrush(wx.Brush(self._bgcolor))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

class MyGrid(gridlib.Grid, glr.GridWithLabelRenderersMixin):
    def __init__(self, *args, **kw):
        gridlib.Grid.__init__(self, *args, **kw)
        glr.GridWithLabelRenderersMixin.__init__(self)

class MyForm(wx.Frame):
    def __init__(self):
        self.sizeX = WIN_SIZE_X
        self.sizeY = WIN_SIZE_Y
        wx.Frame.__init__(self, parent=None,
            title="HexDecBin Calculator " + VERSION,
            size=(self.sizeX, self.sizeY),
            style=wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX)

        #__init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True)
        #curfont = wx.Frame.GetFont(self)
        #curfont.SetPointSize(curfont.GetPointSize())
        #curfont.SetPointSize(12)
        #self.SetFont(curfont)

        #ico = wx.Icon('Minion.ico', wx.BITMAP_TYPE_ICO)
        #self.SetIcon(ico)

        #self.subMuBitLen = wx.Menu()
        #self.subMuBitLen.Append(wx.ID_ANY, '32 bits', kind=wx.ITEM_RADIO)
        #self.subMuBitLen.Append(wx.ID_ANY, '64 bits', kind=wx.ITEM_RADIO)

        self.muFile = wx.Menu()
        self.muAbout= self.muFile.Append(wx.ID_ABOUT, "&About"," Information about this program")
        self.muOnTop = self.muFile.Append(wx.ID_ANY, 'Always On &Top', 'On top window', kind=wx.ITEM_CHECK)
        #self.muBitLen = self.muFile.AppendMenu(wx.ID_ANY, '&Bit Length', self.subMuBitLen)
        self.muReset = self.muFile.Append(wx.ID_ANY, '&Reset All Values\tAlt+R', 'Reset all values')
        self.muExit = self.muFile.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        ###### hot key
        #idAltT = wx.NewId()
        idAltR = wx.NewId()
        #idAltF4 = wx.NewId()
        #self.Bind(wx.EVT_MENU, self.OnTopWin, id=idAltT)
        self.Bind(wx.EVT_MENU, self.OnReset, id=idAltR)
        #self.Bind(wx.EVT_MENU, self.OnExit, id=idAltF4)

        self.accelTbl = wx.AcceleratorTable([(wx.ACCEL_ALT, ord('R'), idAltR)])
                                              #(wx.ACCEL_ALT, ord('T'), idAltT),
                                              #(wx.ACCEL_ALT, ord('X'), idAltF4)
        self.SetAcceleratorTable(self.accelTbl)


        self.mb = wx.MenuBar()
        self.mb.Append(self.muFile, "&File")
        self.SetMenuBar(self.mb)

        panel = wx.Panel(self)

        self.gdBin = MyGrid(panel)
        #self.gdBin = wx.grid.Grid(panel)
        self.gdBin.CreateGrid(2, MAX_BIT_NUM)
        self.gdBin.SetDefaultColSize(20, True)
        self.gdBin.SetDefaultRowSize(20, True)
        self.gdBin.DisableDragGridSize()
        self.gdBin.DisableDragRowSize()
        self.gdBin.DisableDragColSize()
        #self.gdBin.DisableDragCell()
        #self.gdBin.DisableCellEditControl()
        #self.gdBin.ClearSelection()
        self.gdBin.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.gdBin.SetColLabelSize(20)
        self.gdBin.SetRowLabelSize(0)
        self.gdBin.EnableEditing(False)
        self.gdBin.SetDefaultCellBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        self.gdBin.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)


        #LABEL_COLOR_LIST = (wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW), wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT))

        defVal = "0"
        rowIdx = 0
        colorIdx = 1
        for i in range(0, MAX_BIT_NUM):
            colIdx = MAX_BIT_NUM - 1 - i
            self.gdBin.SetColLabelValue(colIdx, str(i))
            self.gdBin.SetCellValue(rowIdx, colIdx, defVal)
            self.gdBin.SetCellAlignment(rowIdx, colIdx, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            self.gdBin.SetCellBackgroundColour(rowIdx, colIdx, wx.WHITE)

            if (i%8 == 0):
                colorIdx = 1 - colorIdx
            self.gdBin.SetColLabelRenderer(colIdx, MyColLabelRenderer(LABEL_COLOR_LIST[colorIdx]))

        #self.gdBin.SetLabelBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWFRAME))

        self.stHex = []
        self.tcHex = []
        self.stDec = []
        self.tcDec = []
        for i in range(0, 2):
            self.stHex.append(wx.StaticText(panel, label="Hex"+str(i+1)+"  "))
            self.tcHex.append(wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, validator = MyValidator(HEX_DIGIT_ONLY)))
            self.tcHex[i].SetMaxLength(ST_HEX_LENGTH)
            self.stDec.append(wx.StaticText(panel, label="Dec"+str(i+1)+"  "))
            self.tcDec.append(wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, validator = MyValidator(DIGIT_ONLY)))
            self.tcDec[i].SetMaxLength(ST_DEC_LENGTH)
        self.tcHex[0].SetFocus()

        self.cbSfMode = wx.CheckBox(panel, label="Subfield mode")

        self.stStartPos = wx.StaticText(panel, label="Start pos ")
        self.tcStartPos = wx.TextCtrl(panel, size=(25,-1), style=wx.TE_PROCESS_ENTER, validator = MyValidator(DIGIT_ONLY))
        self.tcStartPos.SetMaxLength(2)
        self.stEndPos = wx.StaticText(panel, label="End pos ")
        self.tcEndPos = wx.TextCtrl(panel, size=(25,-1), style=wx.TE_PROCESS_ENTER, validator = MyValidator(DIGIT_ONLY))
        self.tcEndPos.SetMaxLength(2)

        self.stSfValHex = wx.StaticText(panel, label="Value: Hex  ")
        self.tcSfValHex = wx.TextCtrl(panel, size=(100,-1), style=wx.TE_PROCESS_ENTER, validator = MyValidator(HEX_DIGIT_ONLY))
        self.tcSfValHex.SetMaxLength(ST_HEX_LENGTH)
        self.stSfValDec = wx.StaticText(panel, label="Dec  ")
        self.tcSfValDec = wx.TextCtrl(panel, size=(100,-1), style=wx.TE_PROCESS_ENTER, validator = MyValidator(DIGIT_ONLY))
        self.tcSfValDec.SetMaxLength(ST_DEC_LENGTH)

        self.stExp = wx.StaticText(panel, label="Expression")
        self.tcExp = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, validator = MyValidator(EXP_CHR_ONLY))

        self.btnExp = wx.Button(panel, size=(30, -1), label="=")
        self.btnLsft = wx.Button(panel, size=(30, -1), label="<<")
        self.btnRsft = wx.Button(panel, size=(30, -1), label=">>")
        self.btnNot = wx.Button(panel, size=(30, -1), label="~")
        self.btnEndian = wx.Button(panel, size=(65, -1), label="BE<->LE")

        self.cbMode = wx.CheckBox(panel, label="Two calc mode")

        self.OneCalcMode()

        ##############################################
        # set control handler
        self.Bind(wx.EVT_MENU, self.OnAbout, self.muAbout)
        self.Bind(wx.EVT_MENU, self.OnTopWin, self.muOnTop)
        self.Bind(wx.EVT_MENU, self.OnReset, self.muReset)
        self.Bind(wx.EVT_MENU, self.OnExit, self.muExit)
        for i in range(0, 2):
            self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextHexEnter, self.tcHex[i])
            self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextDecEnter, self.tcDec[i])
        self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextExpEnter, self.tcExp)

        self.Bind(wx.EVT_BUTTON, self.OnButtonExp, self.btnExp)
        self.Bind(wx.EVT_BUTTON, self.OnButtonLsft, self.btnLsft)
        self.Bind(wx.EVT_BUTTON, self.OnButtonRsft, self.btnRsft)
        self.Bind(wx.EVT_BUTTON, self.OnButtonNot, self.btnNot)
        self.Bind(wx.EVT_BUTTON, self.OnButtonEndian, self.btnEndian)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbMode, self.cbMode)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbSfMode, self.cbSfMode)
        self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextPosEnter, self.tcStartPos)
        self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextPosEnter, self.tcEndPos)
        self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextSfValHexEnter, self.tcSfValHex)
        self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextSfValDecEnter, self.tcSfValDec)
        ##############################################
        # Layout
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.gdBin, 0, wx.CENTER, 20)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(wx.StaticText(panel), 0, border=50)

        sizer2.Add(self.stHex[0], 0, wx.LEFT|wx.CENTER, border=20)
        sizer2.Add(self.tcHex[0], 4, wx.CENTER, border=20)
        sizer2.Add(self.stDec[0], 0, wx.LEFT|wx.CENTER, border=20)
        sizer2.Add(self.tcDec[0], 4, wx.CENTER, border=20)
        sizer2.Add(self.stHex[1], 0, wx.LEFT|wx.CENTER, border=20)
        sizer2.Add(self.tcHex[1], 4, wx.CENTER, border=20)
        sizer2.Add(self.stDec[1], 0, wx.LEFT|wx.CENTER, border=20)
        sizer2.Add(self.tcDec[1], 4, wx.CENTER, border=20)
        sizer2.Add(wx.StaticText(panel), 2, border=20)

        sizer2.Add((-1, 30))

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(self.cbSfMode, 0, wx.CENTER, border=20)
        #sizer4.Add(wx.StaticText(panel), 1, border=20)
        sizer4.Add(self.stStartPos, 0, wx.CENTER|wx.LEFT, border=20)
        sizer4.Add(self.tcStartPos, 0, wx.CENTER, border=20)
        sizer4.Add(self.stEndPos,   0, wx.CENTER|wx.LEFT, border=20)
        sizer4.Add(self.tcEndPos,   0, wx.CENTER, border=20)
        sizer4.Add(self.stSfValHex, 0, wx.CENTER|wx.LEFT, border=20)
        sizer4.Add(self.tcSfValHex, 0, wx.CENTER, border=20)
        sizer4.Add(self.stSfValDec, 0, wx.CENTER|wx.LEFT, border=20)
        sizer4.Add(self.tcSfValDec, 0, wx.CENTER, border=20)
        #sizer4.Add(wx.StaticText(panel), 2, border=20)

        sizer4.Add((-1, 30))

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(wx.StaticText(panel), 0, border=50)
        sizer3.Add(self.stExp, 0, wx.RIGHT|wx.CENTER, border=10)
        sizer3.Add(self.tcExp, 2, wx.CENTER, border=10)
        sizer3.Add(self.btnExp, 0, wx.LEFT, border=10)
        sizer3.Add(self.btnLsft, 0, wx.LEFT, border=10)
        sizer3.Add(self.btnRsft, 0, wx.LEFT, border=10)
        sizer3.Add(self.btnNot, 0, wx.LEFT, border=10)
        sizer3.Add(self.btnEndian, 0, wx.LEFT, border=10)
        sizer3.Add(self.cbMode, 1, wx.LEFT|wx.CENTER, border=10)

        sizer1.Add(sizer2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        sizer1.Add(sizer4, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        sizer1.Add(sizer3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        panel.SetSizer(sizer1)

        self.MODE_VAL = 1 if (self.cbMode.GetValue() == True) else 0
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText(MODE_STATUS_STR[self.MODE_VAL])
        self.SetMaxSize((self.sizeX, self.sizeY))
        self.SetMinSize((self.sizeX, self.sizeY))

    ##############################################
    # Control
    def OnWarnning(self, strMsg):
        dlg = wx.MessageDialog(self, strMsg, "Input error", wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def OnAbout(self, event):
        #dlg = wx.MessageDialog(self, "Hex,Dec,Bin Calculator\nNo copyright.\nAuthor:lunwu.yeh@gmail.com", "HexDecBin Calculator", wx.OK)
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        self.Close(True)

    def OnTopWin(self, event):
        if (self.muOnTop.IsChecked() == True):
            self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX|wx.STAY_ON_TOP)
        else:
            self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX)

    def OnReset(self, event):
        self.cbMode.SetValue(False)
        self.cbSfMode.SetValue(False)

        self.RefreshAllValue(0, 0)

        self.tcHex[0].SetValue("")
        self.tcHex[1].SetValue("")
        self.tcDec[0].SetValue("")
        self.tcDec[1].SetValue("")
        self.tcSfValDec.SetValue("")
        self.tcSfValHex.SetValue("")
        self.tcStartPos.SetValue("")
        self.tcEndPos.SetValue("")
        self.tcExp.SetValue("")

        self.OneCalcMode()

    def EvtTextHexEnter(self, event):
        tcHexIdx = 0
        if (event.GetEventObject() == self.tcHex[0]):
            tcHexIdx = 0
        else:
            tcHexIdx = 1
        decVal = long(event.GetString(), 16)
        self.RefreshAllValue(decVal, tcHexIdx)

    def EvtTextDecEnter(self, event):
        tcDecIdx = 0
        if (event.GetEventObject() == self.tcDec[0]):
            tcDecIdx = 0
        else:
            tcDecIdx = 1
        decVal = long(event.GetString())
        self.RefreshAllValue(decVal, tcDecIdx)

    def EvtTextExpEnter(self, event):
        expStr = event.GetString()
        decVal = self.evalExpStr(expStr)
        if (decVal != -1):
            self.RefreshAllValue(decVal, 0)

    def OnCellLeftClick(self, event):
        curRow = event.GetRow()
        curCol = event.GetCol()
        if (self.cbMode.GetValue() == False and curRow == 1):
            return

        cellVal = 1 - long(self.gdBin.GetCellValue(curRow, curCol))
        self.gdBin.SetCellValue(curRow, curCol, str(cellVal))
        self.gdBin.SetCellBackgroundColour(curRow, curCol, COLOR_LIST[cellVal])

        binStr = ""
        for i in range(0, MAX_BIT_NUM):
            binStr += self.gdBin.GetCellValue(curRow, i)
        decVal = long(binStr, 2)

        self.RefreshAllValue(decVal, curRow)


    def OnButtonExp(self, event):
        expStr = self.tcExp.GetValue()
        decVal = self.evalExpStr(expStr)
        if (decVal != -1):
            self.RefreshAllValue(decVal, 0)

    def OnButtonLsft(self, event):
        expStr = "(" + self.tcHex[0].GetValue() + ") << 1 & " + str(MAX_NUM)
        decVal = self.evalExpStr(expStr)
        self.RefreshAllValue(decVal, 0)

    def OnButtonRsft(self, event):
        expStr = "(" + self.tcHex[0].GetValue() + ") >> 1 & " + str(MAX_NUM)
        decVal = self.evalExpStr(expStr)
        self.RefreshAllValue(decVal, 0)

    def OnButtonNot(self, event):
        expStr = "~(" + self.tcHex[0].GetValue() + ") & " + str(MAX_NUM)
        decVal = self.evalExpStr(expStr)
        self.RefreshAllValue(decVal, 0)

    def OnButtonEndian(self, event):
        hexStr = self.tcHex[0].GetValue()[2:].zfill(HEX_LENGTH)

        resultStr = ""
        for i in reversed(xrange(0, len(hexStr), 2)):
            resultStr += hexStr[i:i+2]

        self.tcHex[0].SetValue(resultStr)
        decVal = long(self.tcHex[0].GetValue(), 16)
        self.RefreshAllValue(decVal, 0)

    def OnCbMode(self, event):
        self.MODE_VAL = 1 if (self.cbMode.GetValue() == True) else 0
        if (event.IsChecked() == True):
            self.TwoCalcMode()
        else:
            self.OneCalcMode()
        self.sb.SetStatusText(MODE_STATUS_STR[self.MODE_VAL])

    def OnCbSfMode(self, event):
        if (event.IsChecked() == True):
            self.SubFieldMode()
        else:
            self.OneCalcMode()


    def CheckSpEp(self):
        strSp = self.tcStartPos.GetValue()
        strEp = self.tcEndPos.GetValue()
        if (strSp == "" or strEp == ""):
            self.OnWarnning("Start or end position is NULL !!!")
            return (-1, -1)

        spVal = int(strSp)
        epVal = int(strEp)
        if (spVal > epVal):
            self.OnWarnning("End position must be greater or equal than start position !!!")
            return (-1, -1)
        elif (epVal > (MAX_BIT_NUM-1)):
            self.OnWarnning("End position must be less or equal than " + str(MAX_BIT_NUM-1))
            return (-1, -1)

        return (spVal, epVal)

    def GetAfterMaskValue(self, decVal, maskVal, shiftVal):
        tmpVal1 = self.LeftShift(decVal, maskVal)
        tmpVal2 = self.RightShift(tmpVal1, maskVal)
        afterMaskDecVal = self.RightShift(tmpVal2, shiftVal)
        return afterMaskDecVal

    def LeftShift(self, decVal, pos):
        return ((decVal << pos) & MAX_NUM)

    def RightShift(self, decVal, pos):
        return ((decVal >> pos) & MAX_NUM)

    def CalcSubFieldValChange(self, sfDecVal):
        # TODO: check max and min value of tcSfValHex and tcSfValDec input string

        spDecVal, epDecVal = self.CheckSpEp()
        if (spDecVal == -1 or epDecVal == -1):
            return

        #strSp = self.tcStartPos.GetValue()
        #strEp = self.tcEndPos.GetValue()
        #decSp = int(strSp)
        #decEp = int(strEp)

        maskDecVal = int(('1' * (epDecVal - spDecVal + 1)), 2)

        if (sfDecVal > maskDecVal):
            self.OnWarnning("Input error. Subfield value is greater than its maximum value.\n"
                    + "Dec:" + str(sfDecVal) + " > " + str(maskDecVal) + "\n"
                    + "Hex: 0x" + str(hex(sfDecVal))[2:].upper() + " > 0x" + str(hex(maskDecVal))[2:].upper())
            return
        print "maskDecVal: %d" % maskDecVal

        afterMaskDecVal = ((~(maskDecVal << spDecVal)) & MAX_NUM)
        tcHex0DecVal = int(self.tcHex[0].GetValue(), 16)
        decVal = ((tcHex0DecVal & afterMaskDecVal) | (sfDecVal << spDecVal))

        checkSfDecVal = self.GetAfterMaskValue(decVal, MAX_BIT_NUM-epDecVal-1, spDecVal)

        if (checkSfDecVal != sfDecVal):
            self.OnWarnning("Fatal error. The result may be wrong.\nPlease contact author.")

        self.SetSfHexDecVal(decVal)
        #hexStr = str(hex(decVal))[2:].upper()
        #if (hexStr[-1] == "L"):
        #    self.tcSfValHex.SetValue("0x" + str(hexStr[:-1]))
        #else:
        #    self.tcSfValHex.SetValue("0x" + str(hexStr))
        #self.tcSfValDec.SetValue(str(decVal))

        # set tcDec[0], and call RefreshAllValue to refresh all field except tcSfHex and tcSfDec
        self.tcDec[0].SetValue(str(decVal))

        self.RefreshAllValue(decVal, 0)

    def SetSfHexDecVal(self, decVal):
        hexStr = str(hex(decVal))[2:].upper()
        if (hexStr[-1] == "L"):
            self.tcSfValHex.SetValue("0x" + str(hexStr[:-1]))
        else:
            self.tcSfValHex.SetValue("0x" + str(hexStr))

        self.tcSfValDec.SetValue(str(decVal))
        return

    def EvtTextSfValHexEnter(self, event):
        sfDecVal = int(self.tcSfValHex.GetValue(), 16)
        self.CalcSubFieldValChange(sfDecVal)
        return

    def EvtTextSfValDecEnter(self, event):
        sfDecVal = int(self.tcSfValDec.GetValue())
        self.CalcSubFieldValChange(sfDecVal)
        return

    def EvtTextPosEnter(self, event):
        self.CalcSubFieldVal()

    def CalcSubFieldVal(self):
        spVal, epVal = self.CheckSpEp()
        if (spVal == -1 or epVal == -1):
            return
        """
        strSp = self.tcStartPos.GetValue()
        strEp = self.tcEndPos.GetValue()
        if (strSp == "" or strEp == ""):
            self.OnWarnning("Start or end position is NULL !!!")
            return

        spVal = int(strSp)
        epVal = int(strEp)
        if (spVal > epVal):
            self.OnWarnning("End position must greater or equal than start position !!!")
            return
        elif (epVal > (MAX_BIT_NUM-1)):
            self.OnWarnning("End position must be less or equal than " + str(MAX_BIT_NUM-1))
            return
        """

        rowIdx = 1
        defVal = ""

        cnt = 0
        binStr = ""
        for i in range(0, MAX_BIT_NUM):
            colIdx = MAX_BIT_NUM - 1 - i
            self.gdBin.SetCellSize(rowIdx, i, 1, 1)
            self.gdBin.SetCellValue(rowIdx, colIdx, defVal)
            self.gdBin.SetCellAlignment(rowIdx, colIdx, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            self.gdBin.SetCellBackgroundColour(rowIdx, colIdx, wx.WHITE)
            if (i >= spVal and i <= epVal):
                self.gdBin.SetCellBackgroundColour(rowIdx, colIdx, wx.GREEN)
                self.gdBin.SetCellValue(rowIdx, colIdx, str(cnt))
                cnt += 1
                binStr += self.gdBin.GetCellValue(0, colIdx)

        decVal = int(binStr[::-1], 2)
        self.SetSubFieldValue(decVal)

        #self.tcSfValHex.SetValue("0x" + hex(decVal)[2:].upper())
        #self.tcSfValDec.SetValue(str(decVal))
    ##############################################
    def SubFieldComponent(self, boolVal):
        self.tcStartPos.Enable(boolVal)
        self.tcEndPos.Enable(boolVal)
        self.tcSfValHex.Enable(boolVal)
        self.tcSfValDec.Enable(boolVal)
        self.cbSfMode.SetValue(boolVal)

    def OneCalcComponent(self, boolVal):
        self.tcHex[1].Enable(boolVal)
        self.tcDec[1].Enable(boolVal)

    def TwoCalcComponent(self, boolVal):
        self.tcHex[1].Enable(boolVal)
        self.tcDec[1].Enable(boolVal)
        self.cbMode.SetValue(boolVal)

    def SubFieldMode(self):
        self.SubFieldComponent(True)
        self.TwoCalcComponent(False)

    def TwoCalcMode(self):
        rowIdx = 1
        defVal = "0"
        for i in range(0, MAX_BIT_NUM):
            self.gdBin.SetCellSize(rowIdx, i, 1, 1)
            self.gdBin.SetCellValue(rowIdx, i, defVal)
            self.gdBin.SetCellAlignment(rowIdx, i, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            self.gdBin.SetCellBackgroundColour(rowIdx, i, wx.WHITE)

        self.TwoCalcComponent(True)
        self.SubFieldComponent(False)

    def OneCalcMode(self):
        rowIdx = 1
        defVal = "0"
        for i in range(0, MAX_BIT_NUM):
            if (i % UNIT_NUM == 0):
                self.gdBin.SetCellSize(rowIdx, i, MERGE_ROW_NUM, MERGE_COL_NUM)
                self.gdBin.SetCellValue(rowIdx, i, defVal)
                self.gdBin.SetCellAlignment(rowIdx, i, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                self.gdBin.SetCellBackgroundColour(rowIdx, i, wx.WHITE)

        self.OneCalcComponent(False)
        self.SubFieldComponent(False)

    def evalExpStr(self, expStr):
        if (expStr == ""):
            return -1
        decVal = eval(expStr)
        if (decVal > 0xFFFFFFFF or decVal < 0):
            self.OnWarnning("The result is overflow or negative !!!")
            return -1
        else:
            return decVal

    def SetTcHexValue(self, decVal, idx):
        hexStr = str(hex(decVal))[2:].upper()
        if (hexStr[-1] == "L"):
            self.tcHex[idx].SetValue("0x" + str(hexStr[:-1]))
        else:
            self.tcHex[idx].SetValue("0x" + str(hexStr))

    def SetTcDecValue(self, decVal, idx):
        self.tcDec[idx].SetValue(str(decVal))

    def Hex2Bin(self, hexStr):
        return bin(long(hexStr, 16))[2:].zfill(MAX_BIT_NUM)

    def Dec2Bin(self, decStr):
        return bin(decStr)[2:].zfill(MAX_BIT_NUM)

    def SetGdBinValue(self, decVal, idx):
        binStr = self.Dec2Bin(decVal)
        rowIdx = idx
        for i in range(0, MAX_BIT_NUM):
            self.gdBin.SetCellValue(rowIdx, i, binStr[i])
            self.gdBin.SetCellBackgroundColour(rowIdx, i, COLOR_LIST[int(binStr[i])])

        if (self.cbMode.GetValue() == False and self.cbSfMode.GetValue() == False):
            self.SetGdBinHexValue()

    def SetGdBinHexValue(self):
        rowIdx = 1
        hexVal = self.tcHex[0].GetValue()[2:].zfill(HEX_LENGTH)
        cnt = 0
        for i in range(0, MAX_BIT_NUM):
            if (i % UNIT_NUM == 0):
                self.gdBin.SetCellValue(rowIdx, i, hexVal[cnt])
                cnt += 1

    def SetSubFieldValue(self, decVal):
        if (self.cbSfMode.GetValue() == True):
            self.tcSfValHex.SetValue("0x" + hex(decVal)[2:].upper())
            self.tcSfValDec.SetValue(str(decVal))

    def RefreshAllValue(self, decVal, idx):
        self.SetTcHexValue(decVal, idx)
        self.SetTcDecValue(decVal, idx)
        self.SetGdBinValue(decVal, idx)
        self.gdBin.ClearSelection()
        if (self.cbSfMode.GetValue() == True):
            self.CalcSubFieldVal()

    #def EvtTextExpChar(self, event):
    #    keycode = event.GetKeyCode()
    #    strKey = chr(keycode)
    #    print "ExpChar:%s, chr:%s" % (keycode, strKey)
    #    event.Skip()

    #def EvtTextExpKeyDown(self, event):
    #    keycode = event.GetKeyCode()
    #    print "KeyDown:%s, chr:%s" % (keycode, chr(keycode))
    #    event.Skip()

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(500, 355)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())

class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About Hex,Dec,Bin Calculator " + VERSION,
            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL)
        hWin = HtmlWindow(self, -1)
        hWin.SetPage(self.aboutText)
        iRep = hWin.GetInternalRepresentation()
        hWin.SetSize((iRep.GetWidth()+25, iRep.GetHeight()+10))
        self.SetClientSize(hWin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

    aboutText = """<p>Hex,Dec,Bin Calculator {ver}.<br>No copyright.<br>
Author:Lun-Wu Yeh, <a href="mailto:lunwu.yeh@gmail.com">lunwu.yeh@gmail.com</a><br>
<b>User guide:</b><br>
1) This calculator can support hex, dec, and binary translation.<br>
2) You can input the hex or dec in textfield and <b>press enter</b> to show the result.<br>
3) You can <b>click any bits on the grid</b> to show the correspond hex or dec.<br>
4) You can click "Two calc mode" to support two numbers.<br>
5) The expression can <b>support +, -, *, /, &, |, ^, (, ), %,&lt;&lt;, &gt;&gt;, hex, and dec.</b><br>
Example: ((0xFE + 4) &lt;&lt; 5) | 0xF0<br>
Note that the numbers in this expression are <b>signed numbers</b> not unsigned numbers.<br>
Also, you should be care the <b>operator precedence</b>.<br>
6) The button '&lt' or '&gt' can left or right shift Dec1 value one byte, respectively.<br>
7) The button '~' can inverse the Dec1 value.<br>
8) The button 'BE&lt;-&gt;LE' can change the endian of the Dec1 value.<br>
9) In Subfield mode, you should input start pos and end pos, <br>
   then <b>press enter in 'Start pos' or 'End pos' field</b>.<br>
   You can get a sub sequence bit numbers of Dec1 value.<br>
10) In menubar (File->Always On Top), you can set it to make the calculator on top window.</p>""".format(ver=VERSION)


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm().Show(True)
    app.MainLoop()
