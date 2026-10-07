import sys
import os
import shutil
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
import socket
import cv2
import argparse
import pathlib
import struct
import threading
import rsa

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
            "math",
            "smile",
            "sendfile", "recvfile",
            "chat"
        ]
        
        self.running_chat_socket = True
        self.sock_chat = None

        self.public_key, self.private_key = rsa.newkeys(1024)
        self.public_partner = None

    def Get_Input(self):
        prompt_text = f"PYSH({os.getcwd()})>>"

        command = input(prompt_text)

        if not command:
            return None

        splitted = command.split()
        base = splitted[0]
        
        if base not in self.commands:
            print(f"unknown command: '{base}', try 'help' for help")
            return None

        return splitted

    def LF(self, command):
        try:
            delimeter = ">"
            if len(command) < 2 and delimeter not in command:
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
            elif len(command) > 1 and delimeter not in command:
                print("specify the folder using '>'")
            elif delimeter in command:
                command = " ".join(command[1:])
                folders = []
                files = []
                if delimeter in command:
                    lf, fold = command.split(delimeter, 1)
                    fold = fold.strip()

                    folder_content = os.listdir(fold)
                    abs_folder = os.path.abspath(fold)

                    print(f"content of: '{abs_folder}'")
                    
                    for item in folder_content:
                        path = os.path.join(fold, item)
                        if os.path.isdir(path):
                            folders.append(item)
                        elif os.path.isfile(path):
                            files.append(item)
                    
                    print("files: ")
                    for file in files:
                        print(f" -{file}")

                    print()

                    print("folders: ")
                    for folder in folders:
                        print(f" -{folder}")
                    
                    print()
        except FileNotFoundError:
            print(f"folder '{command}' does not exist")
        except NotADirectoryError:
            print(f"'{command}' is a file, not directory")
        except OSError as e:
            print(f"{e}")

    def WHO(self):
        comp_name = socket.gethostname()
        host_name = getpass.getuser()
        print(f"{host_name}/{comp_name}")

    def PD(self):
        cwd = os.getcwd()
        print(f"{cwd}")

    def MD(self, folder):
        if len(folder) < 2:
            print(" specify a folder name to make")
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
                print(" specify a folder to remove")
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
            print(" specify a folder path")
        else:
            full_path = " ".join(command[1:])
            try:
                os.chdir(full_path)
            except FileNotFoundError:
                print(f"folder '{full_path}' does not exist")
            except PermissionError:
                print(f"you had no permission to open '{full_path}' folder")
            except OSError as e:
                print(f"{e}")

    def REM(self, command):
        to_remove = " ".join(command[1:])

        if not to_remove:
            print(" specify a file to remove")
            return

        to_remove = [to_remove]

        for rem in to_remove:
            try:
                if rem.startswith("*."):
                    match = glob.glob(rem)
                    if not match:
                        print(f"no file that matches the pattern '{rem}'")
                    else:
                        yn = input(fr"remove all '{os.getcwd()}\{rem}'? (y/n)> ")
                        if yn in ("y", "yes"):
                            for file in match:
                                try:
                                    print(f"removing '{file}' file...")
                                    os.remove(file)
                                except PermissionError:
                                    print(f"you had no permission to remove '{file}' file")
                                except OSError as e:
                                    print(f"{e}")
                        else:
                            return
                else:
                    abs_path = pathlib.Path(rem)
                    if abs_path.is_absolute():
                        if abs_path.is_file():
                            print(f"removing '{abs_path}' file...")
                            abs_path.unlink()
                        elif abs_path.is_dir():
                            print(f"file '{abs_path}' is a directory")
                        else:
                            print(f"no such file found: {abs_path}")
                    else:
                        root_path = pathlib.Path.cwd()
                        matches = [p for p in root_path.rglob(rem) if p.is_file()]

                        if matches:
                            for files in matches:
                                print(f"removing '{files}' file...")
                                files.unlink()
                        elif os.path.isdir(rem):
                            print(f"file '{rem}' is a directory")
                        else:
                            print(f"no such file found: '{rem}'")
                                
            except PermissionError:
                print(f"you had no permission to remove '{rem}' file")
            except OSError as e:
                print(f"{e}")

    def WRITE(self, command):
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
                except IsADirectoryError:
                    print(f"file '{filename}' is a directory")
                except PermissionError:
                    print(f"you had no permission to write '{filename}' file")
                except FileNotFoundError:
                    pass
                except OSError as e:
                    print(f"{e}")
            else:
                print(f"{command}")

    def READ(self, command):
        try:
            if len(command) < 2:
                print(" specify a file to read")
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
        except OSError as e:
            print(f"{e}")

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
        arg = command[1:]

        parse = argparse.ArgumentParser(add_help=False)

        parse.add_argument('-ims', '--immediate', action='store_true', dest='immediate')
        parse.add_argument('-k', '--keep', action='store_true', dest='keep')
        parse.add_argument('-s', type=int, default=None, dest='seconds')
        
        try:
            parsed, unknown = parse.parse_known_args(arg)
            unknown = unknown

            if not unknown:
                print("specify a program to execute")
                return

            CREATE_NEW_CONSOLE = 0x00000010

            if parsed.immediate:
                sec = parsed.seconds if parsed.seconds is not None else 5

                process = subprocess.Popen(["cmd.exe", "/k"] + unknown, 
                                        creationflags=CREATE_NEW_CONSOLE, 
                                        stdout=None, stderr=None, stdin=None)
                time.sleep(sec)
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
            elif parsed.keep:
                if parsed.seconds is not None:
                    print("skipping '-s' since keep is running")
                process = subprocess.Popen(["cmd.exe", "/k"] + unknown, 
                                        creationflags=CREATE_NEW_CONSOLE, 
                                        stdout=None, stderr=None, stdin=None)
            else:
                if parsed.seconds is not None:
                    print("skipping '-s' since keep is running")

                print("wrong option, only use:\n"
                      " '-ims' or '--immediate' to immediately close terminal after 5 seconds\n"
                      " '-k' or '--keep' to not immediately close terminal\n"
                      " '-s' to specify the seconds of how long the terminal would appear\n"
                      " Usage: exec <option> <program_name> ('-s <seconds>' only use with '-ims' or '--immediate')")
        except SystemExit:
            print("failed to launch program, due to structural code or options format")
        except FileNotFoundError:
            print(f"program does not exist")
        except OSError:
            print(f"failed to launch program, maybe missing keywords or untrue condition")

    def PK(self, command):
        found = False
        if len(command) < 2:
            print(" specify an image name to kill")
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
                print(" specify a pid name to kill")
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
                print(" specify a folder/file name to move into destinated folder")
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
                        print(" specify the folder destination with '->'")
                else:
                    print(" specify the folder destination with '->'")
        except:
            pass

    def CF(self, command):
        try:
            if len(command) < 2:
                print(" specify a folder/file name to copy into destined folder")
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
                                print(f"'{source}' does not exist, try with 'a<file/foldername>' if it has spaces")
                    else:
                        print(" specify the folder destination with '->'")
                else:
                    print(" specify the folder destination with '->'")
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
        
    def PLAY_AUDIO(self, command):
        try:
            pygame.init()
            pygame.mixer.init()
            
            scr = pygame.display.set_mode((545, 300))
            pygame.display.set_caption("SPACE->pause/play, ESC->quit, left/right->rewind/forward")

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
            song_pos = 0.0
            song_jump = 5.0

            clock = pygame.time.Clock()

            while running:
                dt = clock.tick(60) / 1000.0

                if pygame.mixer.music.get_busy():
                    song_pos += dt

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print("video stopped")
                        running = False

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            print("video stopped")
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

                        elif event.key == pygame.K_LEFT:
                            song_pos -= song_jump
                            if song_pos < 0:
                                song_pos = 0.0
                            pygame.mixer.music.set_pos(song_pos)
                            print(f"rewinded song to: {song_pos:.1f} second")

                        elif event.key == pygame.K_RIGHT:
                            song_pos += song_jump
                            pygame.mixer.music.set_pos(song_pos)
                            print(f"forwarded song to: {song_pos:.1f} second")

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
                print(" specify an audio/video file to play")
            else:
                command = " ".join(command[1:])
                mime = magic.from_file(command, mime=True)

                if mime.startswith("audio/"):
                    self.PLAY_AUDIO(command)
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

    def SMILE(self, command):
        try:
            index_cam = " ".join(command[1:])
            if len(index_cam) < 2:
                print("use 'front' for front camera, and 'back' for back camera")
            else:
                index_cam = index_cam.replace("front", "0").replace("back", "1")
                cap = cv2.VideoCapture(int(index_cam))
                if not cap.isOpened():
                    print("can't access camera")
                    return                
                else:
                    img_count = 0
                    while True:
                        ret, frame = cap.read()

                        if not ret:
                            print("can't get the frames")
                            break

                        cv2.imshow("livecam: ESC -> exit, space -> take photo", frame)

                        key =  cv2.waitKey(1) & 0xFF

                        if key == 27:
                            print("camera stopped")
                            break
                        elif key == 32:
                            img_name = f"cv2_{img_count}.jpg"
                            cv2.imwrite(img_name, frame)
                            print(f"saved image '{img_name}' to disk")
                            img_count += 1
                        
                    cap.release()
                    cv2.destroyAllWindows()
        except ValueError:
            print("use 'front' for front camera, or 'back' for back camera")

    def recv_all(self, sock,  n):
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def SEND_FILE(self, command):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        delimiter = ">"
        delimiter_ip_port = "-"
        client = " ".join(command[1:])
        if delimiter in client:
            if delimiter_ip_port in client:
                file, ip = client.split(delimiter, 1)
                ip, port = ip.split(delimiter_ip_port, 1)
                try:
                    file = file.strip()
                    ip = ip.strip()
                    port = int(port.strip())
                except ValueError:
                    print("port must be integer or not empty")
                    return
                
                print(f"connecting to {ip}:{str(port)}")
                
                try:
                    sock.connect((ip, port))
                except socket.gaierror:
                    print("can't resolve hostname: hostname typed incorrectly")
                    return
                except ConnectionRefusedError:
                    print("the host you are trying to connect to is inactive or refused the connection")
                    return
                except socket.timeout:
                    print("the host you are trying to connect to is timed out")
                except socket.error as e:
                    print(f"{e}")
                    return
                
                buff = 65536

                if not os.path.exists(file) or os.path.isdir(file):
                    try:
                        sock.sendall(struct.pack("Q", 0))
                    except:
                        pass
                    print(f"file '{file}' does not exist")
                    return
                
                filesize = os.path.getsize(filename=file)

                try:
                    sock.sendall(struct.pack("Q", filesize))
                except:
                    print("can't send the file size: host is inactive/refused connection")
                    return

                try:
                    with open(file, "rb") as f:
                        print(f"sending file '{file}'...")
                        while True:
                            try:
                                data = f.read(buff)
                                if not data:
                                    break
                                sock.sendall(data)
                                print(f'sending... {f.tell()}/{filesize} bytes ({f.tell()/filesize*100:.2f}%)', end='\r')
                            except KeyboardInterrupt:
                                print("\nstopped by user request")
                                break
                        print(f"\nsuccessfully sended file '{file}'")
                except PermissionError:
                    print(f"you have no permission to open and send '{file}' file")
                except socket.error as e:
                    print(f"{e}")
            else:
                print("specify the ip and port using '-' (<filename> > <ip> - <port>)")
        else:
            print("specify the filename to ip and port using '>' (<filename> > <ip> - <port>)")

    def RECV_FILE(self, command):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        filename = " ".join(command[1:])
        delimiter = ">"
        delimiter_ip_port = "-"
        if delimiter in filename:
            if delimiter_ip_port in filename:
                file, ip = filename.split(delimiter, 1)
                ip, port = ip.split(delimiter_ip_port, 1)
                try:
                    file = file.strip()
                    ip = ip.strip()
                    port = int(port.strip())
                except ValueError:
                    print("port must be integer or not empty")
                    return
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind((ip, port))
                except socket.gaierror:
                    print("can't resolve hostname: hostname might be typed incorrectly")
                except OSError as e:
                    if e.errno == 98 or e.errno == 10048:
                        print(f"port '{port}' is being used by other application")
                    else:
                        print(f"{e}")
                    return

                print(f"listening for connection at {ip}:{str(port)}")
                sock.listen(1)
                
                try:
                    conn, addr = sock.accept()
                    print(f"accepted connection from {addr}")
                except socket.error as e:
                    print(f"{e}")
                    return
                
                with conn:
                    buff = 65536
                    try:
                        size = self.recv_all(conn, 8)
                        if not size:
                            print("connection closed before sending filesize")
                            return

                        filesize = struct.unpack("Q", size)[0]

                        if filesize == 0:
                            print("the file that is about to be received is a directory or is not exist")
                            return

                        recv = 0
                        with open(file, "wb") as f:
                            print("receiving...")
                            while recv < filesize:
                                try:
                                    to_read = min(buff, filesize - recv)
                                    data = conn.recv(to_read)
                                    if not data:
                                        break
                                    f.write(data)
                                    recv += len(data)
                                    print(f"receiving... {recv}/{filesize} bytes ({recv/filesize*100:.2f}%)'", end='\r')
                                except KeyboardInterrupt:
                                    print("\nstopped by user request")
                                    break
                            if recv == filesize:
                                print(f"\nsuccessfully received file '{file}'")
                            else:
                                print(f"\nsuccessfully received file '{file}' (file might be corrupted): {recv}/{filesize} bytes")
                    except PermissionError:
                        print(f"you had no permission to receive and write '{file}' file")
                    except socket.error as e:
                        print(f"{e}")
            else:
                print("specify the ip and port using '-' (<filename> > <ip> - <port>)")
        else:
            print("specify the filename to ip and port using '>' (<filename> > <ip> - <port>)")

    def SEND_MSG(self, sock):
        from prompt_toolkit.patch_stdout import patch_stdout

        print("\ntype 's_exit' to exit")
        try:
            while self.running_chat_socket:
                try:
                    with patch_stdout():
                        msg = input("chat> ").strip()

                    if not self.running_chat_socket:
                        break
                    
                    if not msg:
                        continue

                    if msg.lower() == "s_exit":
                        print("\nclosing chat")
                        self.running_chat_socket = False
                        try:
                            sock.shutdown(socket.SHUT_RDWR)
                        except:
                            pass
                        return

                    if not self.public_partner:
                        print("\nno public partner key available")
                        break

                    msg_byte = msg.encode()
                    if len(msg_byte) > 117:
                        print("\nthe limit of rsa 1024 byte encryption is 117 byte per-message")
                        continue

                    sock.send(rsa.encrypt(msg_byte, self.public_partner))
                    print(f"\nyou: '{msg}'")
                except rsa.OverflowError:
                    print("\nmessage length exceeds encryption limit")
                except (socket.error, BrokenPipeError, OSError):
                    self.running_chat_socket = False
                    break
                except (KeyboardInterrupt, EOFError, RuntimeError):
                    self.running_chat_socket = False
                    break
        finally:
            self.running_chat_socket = False

            try:
                sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
    
    def RECV_MSG(self, sock):
        from prompt_toolkit.patch_stdout import patch_stdout

        while self.running_chat_socket:
            try:
                data = sock.recv(1024)
                if not data:
                    with patch_stdout():
                        print("\nchat closed connection")
                    self.running_chat_socket = False
                    break
                data = rsa.decrypt(data, self.private_key)
                data = data.decode()

                with patch_stdout():
                    print(f"\nclient: {data}")

            except rsa.DecryptionError:
                with patch_stdout():
                    print("\nfailed to decrypt message")
            except (socket.error, OSError):
                self.running_chat_socket = False
                break
            
        self.running_chat_socket = False
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except:
            pass

    def CHAT(self, command):
        self.sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        option = " ".join(command[1:])
        host = "host"
        connect = "connect"

        if host in option:
            choice_ip = input("(enter your ip address or type 'global' for global hosting)> ")

            if not choice_ip:
                print("specify the ip first")
                return
            
            choice_port = input("(enter your port)> ")

            if not choice_port:
                print("specify the port")
                return
            
            if choice_ip == "global":
                choice_ip = "0.0.0.0"
            try:
                self.sock_chat.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock_chat.bind((choice_ip, int(choice_port)))
            except socket.gaierror:
                print("can't resolve hostname: hostname might be typed incorrectly")
            except OSError as e:
                if e.errno == 98 or e.errno == 10048:
                    print(f"port '{str(choice_port)}' is being used by other application")
                else:
                    print(f"{e}")
                return
            except ValueError:
                print("the port must be integer or not empty")
                return
            except OverflowError:
                print("port must be 1-65535")
                return

            try:
                print(f"listening for connection at: '{choice_ip}:{str(choice_port)}'")
                self.sock_chat.listen(1)
            except OSError as e:
                if e.errno == 10022:
                    print(f"the ip is wrong, check the typing")
                else:
                    print(f"{e}")
                return
            
            try:
                sock, addr = self.sock_chat.accept()
                sock.sendall(self.public_key.save_pkcs1(format="PEM"))
                self.public_partner = rsa.PublicKey.load_pkcs1(sock.recv(1024))
                print(f"accepted connection from: {addr}")
            except socket.error as e:
                print(f"{e}")
                return

        elif connect in option:
            choice_ip = input("(enter the ip address you want to connect to)> ")

            if not choice_ip:
                print("specify the ip first")
                return

            choice_port = input("(enter the port)> ")

            if not choice_port:
                print("specify the port")
                return
            
            print(f"connecting to: {choice_ip}:{str(choice_port)}")
            
            try:
                sock = self.sock_chat
                sock.connect((choice_ip, int(choice_port)))
                self.public_partner = rsa.PublicKey.load_pkcs1(sock.recv(1024))
                sock.sendall(self.public_key.save_pkcs1(format="PEM"))
            except socket.gaierror:
                print("can't resolve hostname: hostname typed incorrectly")
                return
            except ConnectionRefusedError:
                print("the host you are trying to connect to is inactive or refused the connection")
                return
            except socket.timeout:
                print("the host you are trying to connect to is timed out")
            except socket.error as e:
                print(f"{e}")
                return
            except ValueError:
                print("the port must be integer or not empty")
                return
            except OSError as e:
                print(f"{e}")
                return
            except OverflowError:
                print("port must be 1-65535")
                return

            print(f"connected to: {choice_ip}:{str(choice_port)}")
        else:
            print("use 'host' to host a chat or 'connect' to connect to host")
            return

        self.running_chat_socket = True

        t1 = threading.Thread(target=self.SEND_MSG, args=(sock,), daemon=True)
        t2 = threading.Thread(target=self.RECV_MSG, args=(sock,), daemon=True)

        t1.start()
        t2.start()

        try:
            while self.running_chat_socket:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running_chat_socket = False

        try:
            sock.shutdown(socket.SHUT_RDWR)
        except:
            pass

        t1.join(timeout=1.0)
        t2.join(timeout=0.5)

        try:
            sock.close()
        except:
            pass

    def Run_Command(self):
        try:
            command = self.Get_Input()
            folder = [name.strip() for name in command]

            if command[0] is None:
                pass
            
            elif command[0] in ('exit', 'quit'):
                sys.exit()

            elif command[0] == "help":
                print('''"""
help:
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
 -cf/mf     --> copy (cf) or move (mf) a file/folder into the specified folder (with '->')
 -play      --> play a video/audio file
 -math      --> calculate numbers directly on terminal
 -smile     --> open camera and take a picture (use 'front' for front camera and 'back' for back camera)
 -sendfile  --> send local file directly to host (host must be active and listening for connection)
 -recvfile  --> recv remote file from client (client must send a singular file with same extension and not a directory)
 -chat      --> chat with someone in an encrypted tcp socket on terminal
                """'''.strip('"'))

            elif command[0] == "who?":
                self.WHO()

            elif command[0] == "lf":
                self.LF(command)

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

            elif command[0] == "smile":
                self.SMILE(command)

            elif command[0] == "sendfile":
                self.SEND_FILE(command)

            elif command[0] == "recvfile":
                self.RECV_FILE(command)

            elif command[0] == "chat":
                self.CHAT(command)

        except TypeError:
            pass
        except KeyboardInterrupt:
            print("\n")
            pass

print("PYSH shell terminal (c) average-joe44")
print("type 'help' for more help!")

pysh = Shell()

while True:
    pysh.Run_Command()
