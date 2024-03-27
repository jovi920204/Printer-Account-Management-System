import win32print
import win32api
import win32con
import sched, time
import os
import subprocess
from dependencies import preference_window_autoclick
from multiprocessing import Process

class Work:
    '''
        顏色: 
            win32con.DMCOLOR_COLOR          彩色
            win32con.DMCOLOR_MONOCHROME     灰階
        雙面: 
            win32con.DMDUP_SIMPLEX          單面
            win32con.DMDUP_VERTICAL         以短邊翻面
            win32con.DMDUP_HORIZONTAL       以長邊翻面
        大小:
            win32con.DMPAPER_A3             A3
            win32con.DMPAPER_A4             A4
    '''
    def __init__(self, file: str, color: int, copies: int, duplex: int, size: int):
        self.file = file
        self.color = color
        self.copies = copies
        self.duplex = duplex
        self.size = size

class Printer:
    def __init__(self, name):
        self.name = name
        self.works = []
        self.errorWorks = []
        PRINTER_DEFAULTS = {"DesiredAccess":win32print.PRINTER_ALL_ACCESS}
        self.pHandle = win32print.OpenPrinter(name, PRINTER_DEFAULTS)
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def AddWork(self, work: Work):
        self.works.append(work)
        print(f"Add work to {self.name}")
        self.UpdateWorks(self.scheduler)
        self.scheduler.run()
            

    def PopWork(self):
        if self.works.__len__() > 0:
            work: Work = self.works[0]
            print(f"Pop work at {self.name} - {work}")
            try:
                # 設定參數
                properties = win32print.GetPrinter(self.pHandle, 2)
                properties['pDevMode'].Color = work.color
                properties['pDevMode'].Copies = work.copies
                properties['pDevMode'].Duplex = work.duplex
                properties['pDevMode'].PaperSize = work.size

                ### 2023/8/24 11:32 無法正確設定 PaperSize，即使 print(PaperSize) 值是對的。
                ### Can't set PaperSize correctly.
                ### 2023/8/28 12:00 已解決
                win32print.SetPrinter(self.pHandle, 2, properties, 0)

                # 執行 preference_window_autoclick.py -> 關閉印表機的喜好設定
                Process(target=preference_window_autoclick.run).start()
                # 設定列印機屬性
                win32print.DocumentProperties(0, self.pHandle, self.name, None, None, 5)
                # REF: https://stackoverflow.com/questions/5555453/python-win32print-changing-advanced-printer-options

                print(f"Set properties to {self.name}")
                # 開始列印
                win32print.SetDefaultPrinter(self.name)

                # 將檔案路徑轉為絕對路徑
                path_for_file = rf'{os.getcwd()}\user_files\{work.file}'
                
                # 執行 preference_window_autoclick.py -> 關閉 adobe 顯示的視窗 讓後端可以繼續執行
                Process(target=preference_window_autoclick.run).start()
                subprocess.call(f'Acrobat.exe.lnk /t {path_for_file}', shell=True)

                print(f"Print work in {self.name}")
                self.works.pop()
                return True
            except Exception as e:
                print("ERROR: Pop work failed")
                print(e)
                self.errorWorks.append(work)
                return False
        else:
            return False

    def PrintQueue(self):
        for i in range(len(self.works)):
            work = self.works[i]
            print(str(i+1) + ": " + str(work))

    def GetStatusStr(self):
        properties = win32print.GetPrinter(self.pHandle, 2)
        status = properties['Status']

        #https://github.com/mhammond/pywin32/blob/main/win32/src/win32print/win32print.cpp
        if status == 0:
            return "Idle"
        elif status == win32print.PRINTER_STATUS_PAUSED:
            return "Paused"
        elif status == win32print.PRINTER_STATUS_ERROR:
            return "Error"
        elif status == win32print.PRINTER_STATUS_PENDING_DELETION:
            return "Pending Deletion"
        elif status == win32print.PRINTER_STATUS_PAPER_JAM:
            return "Paper Jam"
        elif status == win32print.PRINTER_STATUS_PAPER_OUT:
            return "Paper Out"
        elif status == win32print.PRINTER_STATUS_MANUAL_FEED:
            return "Manual Feed"
        elif status == win32print.PRINTER_STATUS_PAPER_PROBLEM:
            return "Paper Problem"
        elif status == win32print.PRINTER_STATUS_OFFLINE:
            return "Offline"
        elif status == win32print.PRINTER_STATUS_IO_ACTIVE:
            return "IO Active"
        elif status == win32print.PRINTER_STATUS_BUSY:
            return "Busy"
        elif status == win32print.PRINTER_STATUS_PRINTING:
            return "Printing"
        elif status == win32print.PRINTER_STATUS_OUTPUT_BIN_FULL:
            return "Output Bin Full"
        elif status == win32print.PRINTER_STATUS_NOT_AVAILABLE:
            return "Not Available"
        elif status == win32print.PRINTER_STATUS_WAITING:
            return "Waiting"
        elif status == win32print.PRINTER_STATUS_PROCESSING:
            return "Processing"
        elif status == win32print.PRINTER_STATUS_INITIALIZING:
            return "Initializing"
        elif status == win32print.PRINTER_STATUS_WARMING_UP:
            return "Warming Up"
        elif status == win32print.PRINTER_STATUS_TONER_LOW:
            return "Toner Low"
        elif status == win32print.PRINTER_STATUS_NO_TONER:
            return "No Toner"
        elif status == win32print.PRINTER_STATUS_PAGE_PUNT:
            return "Page Punt"
        elif status == win32print.PRINTER_STATUS_USER_INTERVENTION:
            return "User Intervention"
        elif status == win32print.PRINTER_STATUS_OUT_OF_MEMORY:
            return "Out of Memory"
        elif status == win32print.PRINTER_STATUS_DOOR_OPEN:
            return "Door Open"
        elif status == win32print.PRINTER_STATUS_SERVER_UNKNOWN:
            return "Server Unknown"
        elif status == win32print.PRINTER_STATUS_POWER_SAVE:
            return "Power Save"   
        else:
            return "Unknown"
    
    def IsPrinterError(self):
        properties = win32print.GetPrinter(self.pHandle, 2)
        status = properties['Status']
        
        #https://learn.microsoft.com/en-us/troubleshoot/windows/win32/printer-print-job-status#determine-the-state-of-a-physical-printer
        if status == win32print.PRINTER_STATUS_ERROR:
            return True
        elif status == win32print.PRINTER_STATUS_PAPER_JAM:
            return True
        elif status == win32print.PRINTER_STATUS_PAPER_OUT:
            return True
        elif status == win32print.PRINTER_STATUS_PAPER_PROBLEM:
            return True
        elif status == win32print.PRINTER_STATUS_OUTPUT_BIN_FULL:
            return True
        elif status == win32print.PRINTER_STATUS_NOT_AVAILABLE:
            return True
        elif status == win32print.PRINTER_STATUS_NO_TONER:
            return True
        elif status == win32print.PRINTER_STATUS_OUT_OF_MEMORY:
            return True
        elif status == win32print.PRINTER_STATUS_OFFLINE:
            return True
        elif status == win32print.PRINTER_STATUS_DOOR_OPEN:
            return True
        else:
            return False
            
    def IsPrinterIdle(self):
        properties = win32print.GetPrinter(self.pHandle, 2)
        status = properties['Status']
        return (status == 0)

    def UpdateWorks(self, scheduler):
        if self.works.__len__() > 0:
            if (not self.IsPrinterError()):
                if self.IsPrinterIdle():
                    self.PopWork()
                else:
                    #Update if there's work not done
                    scheduler.enter(5, 1, self.UpdateWorks, (self.scheduler,))
            else:
                print("ERROR: Printer Error Status - " + self.GetStatusStr())

if __name__ == '__main__':
    printer = Printer('C360I-140.118.41.251')
    print(printer.GetStatusStr())
    work = Work('GDSC.pdf', win32con.DMCOLOR_COLOR,1,win32con.DMDUP_VERTICAL, win32con.DMPAPER_A4)
    printer.AddWork(work)
