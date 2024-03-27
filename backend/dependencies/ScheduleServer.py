from dependencies.Printer import Printer, Work
# from Printer import Printer, Work # python ScheduleServer.py 測試用
import win32print
import win32con


class ScheduleServer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.printers = []
        self.i = 0
        for printer in win32print.EnumPrinters(2):
            try:
                newPrinter = Printer(printer[2])
                self.printers.append(newPrinter)
            except:
                print(f"ERROR: Init Printer - {printer[2]} failed")

    def GetAllPrintersName(self):
        return [printer.name for printer in self.printers]

    def AddWorkToPrinter(self, printer: int, work: Work):
        try:
            self.printers[printer].AddWork(work)
            return True
        except:
            return False


if __name__ == '__main__':
    scheduleServer = ScheduleServer()
    print(scheduleServer.GetAllPrintersName())
    work = Work('B11015030.pdf', win32con.DMCOLOR_COLOR,1,win32con.DMDUP_VERTICAL, win32con.DMPAPER_A4)
    scheduleServer.AddWorkToPrinter(4, work)


# 刪除印表機連接埠的方法 https://jengting.blogspot.com/2016/05/Windows-delete-PrinterName-In-PrintPort.html