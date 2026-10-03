import sys
import os
import shutil
from colorama import Fore, Style
import getpass
import psutil
import subprocess
import shlex
import pygame
import magic
import vlc
import keyboard
import time
import glob
import re

class Shell:
    def __init__(self):
        self.commands = [
            "lf",
            "pd",
            "who?",
            "md",
            "rd",
            "exit", "quit",
            "cd",
            "rem",
            "write",
            "read",
            "clear",
            "help",
            "exec", "pk", "pdk", "plist",
            "mf", "cf", "rf",
            "play",
            "math"
        ]

    def Get_Input(self):
        command = input(f"{Fore.GREEN}PYSH({os.getcwd()})>> {Style.RESET_ALL}").strip()

        if not command:
            return None

        splitted = command.split()
        base = splitted[0]
        
        if base not in self.commands:
            print(f"unknown command: '{base}', try 'help' for help")
            return None

        return splitted

    def LF(self):
        folders = []
        files = []

        for item in os.listdir('.'):
            if os.path.isdir(item):
                folders.append(f"{item}")
            elif os.path.isfile(item):
                files.append(f"{item}")

        print("files: ")
        for file in files:
            print(f" -{file}")

        print()

        print("folders: ")
        for folder in folders:
            print(f" -{folder}")
        
        print()

    def WHO(self):
        print(getpass.getuser())

    def PD(self):
        cwd = os.getcwd()
        print(f"{cwd}")

    def MD(self, folder):
        if len(folder) < 2:
            print("please specify a folder name to make")
        else:
            for folders in folder[1:]:
                if not os.path.exists(folders):
                    os.mkdir(folders)
                    print(f"making directory: '{folders}'")
                else:
                    print(f"folder '{folders}' already exist")

    def RD(self, folder):
        try:
            if len(folder) < 2:
                print("please specify a folder to remove")
            else:
                for rfold in folder[1:]:
                    if os.path.exists(rfold):
                        shutil.rmtree(rfold)
                        print(f"removing directory: '{rfold}'")
                    else:
                        print(f"folder '{rfold}' does not exist")
        except NotADirectoryError:
            print(f"folder '{rfold}' is not a directory")

    def CD(self, command):
        if len(command) < 2:
            print("please specify a folder path")
        else:
            full_path = " ".join(command[1:])
            try:
                os.chdir(full_path)
            except FileNotFoundError:
                print(f"folder '{full_path}' does not exist")
            except PermissionError:
                print(f"you had no permission to open '{full_path}' folder")

    def REM(self, command):
        try:
            if len(command) < 2:
                print("please specify a file to remove")
            else:
                for rem in command:
                    if os.path.exists(rem) and os.path.isfile(rem):
                        print(f"removing '{rem}' file...")
                        os.remove(rem)
                    elif rem.startswith("*."):
                        for file in glob.glob(f"*{rem}"):
                            print(f"removing '{file}' file...")
                            os.remove(file)
        except FileNotFoundError:
            print(f"file '{rem}' does not exist")
        except IsADirectoryError:
            print(f"file '{rem}' is a directory")
        except PermissionError:
            print(f"you had no permission to remove '{rem}' file")

    def WRITE(self, command):
        try:
            if len(command) < 2:
                print("WRITE SAY")
            else:
                command = " ".join(command[1:])
                delimiter = ">"
                if delimiter in command:
                    content, filename = command.split(delimiter, 1)
                    con = content.strip()
                    file = filename.strip()
                    try:
                        with open(file, "w") as f:
                            f.write(con)
                    except Exception:
                        pass
                else:
                    print(f"{command}")
        except:
            pass

    def READ(self, command):
        try:
            if len(command) < 2:
                print("please specify a file to read")
            else:
                for files in command[1:]:
                    with open(files, "rb") as f:
                        f_raw = f.read()
                        f_decode = f_raw.decode(errors="replace")

                        sys.stdout.write(f_decode)
                        sys.stdout.flush()
                        print("\n")
        except FileNotFoundError:
            print(f"file '{files}' does not exist")
        except PermissionError:
            print(f"you had no permission to read '{files}' file")
        except IsADirectoryError:
            print(f"file '{files}' is a directory")

    def PLIST(self):
        print("PIDS     |              NAME              |   STATUS  |")
        print("=======================================================")
        for prog in psutil.process_iter(['pid', 'name', 'status']):
            try:
                info = prog.info
                print(f"{info['pid']:<8} | {info['name']:<30} | {info['status']:<10}|")
            except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
                pass
        print("=======================================================")

    def EXEC(self, command):
        try:
            if len(command) < 2:
                print("specify a program name to execute with")
            else:
                CREATE_NEW_CONSOLE = 0x00000010
                subprocess.Popen(command[1:], creationflags=CREATE_NEW_CONSOLE, 
                                stdout=None,
                                stderr=None,
                                stdin=None)
        except FileNotFoundError:
            print(f"program '{command[1]}' does not exist")
        except OSError:
            print(f"failed to launch program '{command[1]}', maybe missing keywords or untrue condition")

    def PK(self, command):
        found = False
        if len(command) < 2:
            print("please specify an image name to kill")
        else:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == command[1]:
                        print(f"process found: '{proc.info['name']}:{proc.info['pid']}', killing it...")
                        proc.kill()
                        found = True
                except psutil.NoSuchProcess:
                    continue
                except psutil.AccessDenied:
                    print(f"you had no permission to kill '{proc.info['name']}' program")
                except psutil.ZombieProcess:
                    print(f"program '{proc.info['name']}' is a zombie process")
            if not found:
                print("no such process found")

    def PDK(self, command):
        try:
            if len(command) < 2:
                print("please specify a pid name to kill")
            else:
                command = int(command[1])
                process = psutil.Process(command)
                program = process.name()
                print(f"process found: '{program}:{process}', killing it...")
                process.kill()
        except ValueError:
            print("the process must be pid (integer), not an image (string)")
        except psutil.AccessDenied:
            print(f"you had no permission to kill '{program}' program")
        except psutil.NoSuchProcess:
            print("no such process found")
        except psutil.ZombieProcess:
            print(f"program '{program}' is a zombie process")

    def MF(self, command):
        try:
            if len(command) < 2:
                print("please specify a folder/file name to move into destinated folder")
            else:
                command = " ".join(command[1:])
                delimiter = "->"
                if delimiter in command:
                    files, dstn = command.split(delimiter, 1)
                    dst = dstn.strip()
                    path_to_move = shlex.split(files)

                    if dst:
                        os.makedirs(dst, exist_ok=True)
                        for source in path_to_move:
                            if os.path.exists(source):
                                item = os.path.basename(source)
                                dstnt = os.path.join(dst, item)
                                print(f"moving '{dstnt}' to '{dst}'...")
                                shutil.move(source, dstnt)
                            else:
                                print(f'"{source}" does not exist, try with "<file/foldername>" if it has spaces')
                    else:
                        print("please specify the folder destination with '->'")
                else:
                    print("please specify the folder destination with '->'")
        except:
            pass

    def CF(self, command):
        try:
            if len(command) < 2:
                print("please specify a folder/file name to copy into destined folder")
            else:
                command = " ".join(command[1:])
                delimiter = "->"
                if delimiter in command:
                    files, dstn = command.split(delimiter, 1)
                    dst = dstn.strip()
                    path_to_move = shlex.split(files)

                    if dst:
                        os.makedirs(dst, exist_ok=True)
                        for source in path_to_move:
                            if os.path.exists(source):
                                item = os.path.basename(source)
                                dstnt = os.path.join(dst, item)
                                print(f"copying '{dstnt}' to '{dst}'...")
                                shutil.copy(source, dstnt)
                            else:
                                print(f'"{source}" does not exist, try with "<file/foldername>" if it has spaces')
                    else:
                        print("please specify the folder destination with '->'")
                else:
                    print("please specify the folder destination with '->'")
        except:
            pass

    def RF(self, command):
        command = " ".join(command[1:])
        try:
            delimiter = " "
            if delimiter in command:
                source, new = command.split(delimiter, 1)
                src = source.strip()
                new = new.strip()
                if os.path.exists(src):
                    print(f"renaming '{src}' to '{new}'...")
                    os.rename(src, new)
                else:
                    print(f"'{src}' does not exist")
        except ValueError:
            pass
        except FileNotFoundError:
            pass        
        except FileExistsError:
            print(f"'{src}' already exist")
        
    def PLAY(self, command):
        try:
            pygame.init()
            pygame.mixer.init()
            
            scr = pygame.display.set_mode((545, 300))
            pygame.display.set_caption("SPACE -> pause/play, ESC -> quit")

            BG = (30, 30, 40)
            CT = (255, 255, 255)
            CH = (46, 204, 113)

            FT = pygame.font.SysFont("Arial", 32, bold=True)
            FS = pygame.font.SysFont("Calibri", 20)

            TT = FT.render("NOW PLAYING:", True, CT)
            TH = FS.render(f"{command}", True, CH)

            pygame.mixer.music.load(f"{command}")
            pygame.mixer.music.play()

            pause = False
            running = True

            clock = pygame.time.Clock()

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.mixer.music.stop()
                            running = False

                        elif event.key == pygame.K_SPACE:
                            if pause:
                                pygame.mixer.music.unpause()
                                print("music resumed")
                                pause = False
                            else:
                                pygame.mixer.music.pause()
                                print("music paused")
                                pause = True
                    scr.fill(BG)
                    scr.blit(TT, (150, 100))
                    scr.blit(TH, (50, 160))
                    pygame.display.flip()

                    clock.tick(60)

            pygame.quit()
        
        except pygame.error as e:
            print(f"{e}")

    def toggle_pause(self):
        global player
        if player is None:
            return None

        if player.is_playing():
            player.pause()
            print("video paused")
        else:
            player.play()
            print("video resumed")

    def toggle_stop(self):
        global player, running

        if player is not None:
            player.stop()
            print("video stopped")
        running = False

    def PLAY_VIDEO(self, command):
        global player, running

        running = True

        instance = vlc.Instance('--quiet')
        player = instance.media_player_new()
        media = instance.media_new(command)
        player.set_media(media)

        player.play()

        time.sleep(1)

        print("press space to pause/resume")
        print("press escape to exit")

        keyboard.add_hotkey('space', self.toggle_pause, suppress=True)
        keyboard.add_hotkey('esc', self.toggle_stop, suppress=True)

        try:
            while running:
                stat = player.get_state()
                if stat == vlc.State.Ended:
                    print("video ended")
                    break
                elif stat == vlc.State.Error:
                    print("an error occured when playing this media")
                    break

                time.sleep(0.1)

        except KeyboardInterrupt:
            pass
        finally:
            if player is not None:
                player.stop()
            keyboard.unhook_all()


    def is_file_audio_or_video(self, command):
        try:
            if len(command) < 2:
                print("please specify an audio/video file to play")
            else:
                command = " ".join(command[1:])
                mime = magic.from_file(command, mime=True)

                if mime.startswith("audio/"):
                    self.PLAY(command)
                elif mime.startswith("video/"):
                    self.PLAY_VIDEO(command)
                else:
                    print(f"file '{command}' is not an audio/video file")
        except FileNotFoundError:
            print(f"file '{command}' audio/video does not exist")
        except OSError as e:
            print(f"{e}")

    def MATH(self, command):
        command = " ".join(command[1:])
        expression = command.replace('x', "*").replace('X', "*")

        if re.match(r"^[\d\s+\-*/.]+$", expression):
            try:
                result = eval(expression)
                print(f"{result}")
            except ZeroDivisionError:
                print("cannot divide numbers by 0")
            except SyntaxError:
                print("the syntax must be: <numbers> <operator> <numbers>")
        else:
            print(f"unknown expression: '{expression}', only use (x, +, -, and /)")

    def Run_Command(self):
        try:
            command = self.Get_Input()
            folder = [name.strip() for name in command]

            if command[0] is None:
                pass
            
            elif command[0] in ('exit', 'quit'):
                sys.exit()

            elif command[0] == "help":
                print("help:")
                print('''"""
                -help      --> help
                -exit/quit --> exit the shell
                -clear     --> clear the terminal screen
                -lf        --> list the files/folders in a folder
                -pd        --> print the current working directory
                -who?      --> shows the current user name
                -md/rd     --> make(md) or remove(rd) directories
                -rf        --> rename a directory or a file
                -cd        --> change the working directory
                -rem       --> remove file(s)
                -write     --> print a text or pipe a text (with '>') into a file
                -read      --> read and print the content of a file(s)
                -exec      --> run internal windows system cmd/powershell only commands
                -plist     --> list programs
                -pk/pdk    --> kill a program by (pk: image_name) or (pdk: pid_name)
                -cf/mf     --> copy (cf) or move (mf) a file into a specified folder (with '->')
                -play      --> play a video/audio file
                -math      --> calculate numbers directly on terminal
                """'''.strip('"'))

            elif command[0] == "who?":
                self.WHO()

            elif command[0] == "lf":
                self.LF()

            elif command[0] == "pd":
                self.PD()

            elif command[0] == "md":
                self.MD(folder)

            elif command[0] == "rd":
                self.RD(folder)

            elif command[0] == "cd":
                self.CD(command)

            elif command[0] == "rem":
                self.REM(command)

            elif command[0] == "write":
                self.WRITE(command)

            elif command[0] == "read":
                self.READ(command)

            elif command[0] == "clear":
                os.system('cls')

            elif command[0] == "exec":
                self.EXEC(command)

            elif command[0] == "pk":
                self.PK(command)
            
            elif command[0] == "pdk":
                self.PDK(command)

            elif command[0] == "plist":
                self.PLIST()

            elif command[0] == "mf":
                self.MF(command)

            elif command[0] == "cf":
                self.CF(command)

            elif command[0] == "rf":
                self.RF(command)

            elif command[0] == "play":
                self.is_file_audio_or_video(command)

            elif command[0] == "math":
                self.MATH(command)

        except TypeError:
            pass
        except KeyboardInterrupt:
            print("\n")
            pass

print("PYSH shell terminal (c) average-joe44")
print("type 'help' for more help!")
while True:
    Shell().Run_Command()