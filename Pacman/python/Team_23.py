from dis import show_code
import random
import threading
import STcpClient
import time
import sys

class MyThread(threading.Thread): 
   def __init__(self, *args, **keywords): 
       threading.Thread.__init__(self, *args, **keywords) 
       self.killed = False      
   def start(self):         
       self.__run_backup = self.run         
       self.run = self.__run                
       threading.Thread.start(self)         
   def __run(self):         
       sys.settrace(self.globaltrace)         
       self.__run_backup()         
       self.run = self.__run_backup         
   def globaltrace(self, frame, event, arg):         
       if event == 'call':             
           return self.localtrace         
       else:             
           return None        
   def localtrace(self, frame, event, arg):         
       if self.killed:             
          if event == 'line':                 
              raise SystemExit()         
       return self.localtrace         
   def kill(self):         
       self.killed = True

def H_of_n(start,destination):
    M_distance = abs(start[0] - destination[0]) +  abs(start[1] - destination[1])  
    return M_distance

def backtrace(start,destination):
        now_point_x = destination[0]
        now_point_y = destination[1]
        first_direction = ''
        while(now_point_x!=start[0] or now_point_y !=start[1] and (now_point_x,now_point_y) in direction):
            if(direction[(now_point_x,now_point_y)] == 'r'):
                now_point_y -= 1
                first_direction = 'r'
                continue
            if(direction[(now_point_x,now_point_y)] == 'l'):
                now_point_y += 1
                first_direction = 'l'
                continue
            if(direction[(now_point_x,now_point_y)] == 'u'):
                now_point_x += 1
                first_direction = 'u'
                continue
            if(direction[(now_point_x,now_point_y)] == 'd'):
                now_point_x -= 1
                first_direction = 'd'
                continue
        return first_direction



def G_of_n(start,destination):
        # start = [3,5]
        # destination = [9,18]
        
        queue = []
        visit = []
        global direction
        direction = {}
        distance = 0
        queue.append(start)
        while(len(queue)!= 0 ):
            for i in range(len(queue)):
                node = queue.pop(0)
                if(node[0] == destination[0] and node[1]==destination[1]):
                    return distance,backtrace(start,destination)
                # left
                if([node[0],node[1]-1] not in visit and node[1]-1 >= 0 and parallel_wall[node[0]][node[1]] != 1):
                    # print('from',node[0],' ',node[1])
                    # print('to',node[0],' ',node[1]-1)
                    visit.append([node[0],node[1]-1])
                    queue.append([node[0],node[1]-1])
                    direction[(node[0],node[1]-1)] = 'l'
                # right
                if([node[0],node[1]+1] not in visit and node[1]+1 < 16 and parallel_wall[node[0]][node[1]+1] != 1):
                    visit.append([node[0],node[1]+1])
                    queue.append([node[0],node[1]+1])
                    # print('from',node[0],' ',node[1])
                    # print('to',node[0],' ',node[1]+1)
                    direction[(node[0],node[1]+1)] = 'r'
                # up
                if([node[0]-1,node[1]] not in visit and node[0]-1 >= 0 and vertical_wall[node[0]][node[1]] != 1):
                    visit.append([node[0]-1,node[1]])
                    queue.append([node[0]-1,node[1]])
                    # print('from',node[0],' ',node[1])
                    # print('to',node[0]-1,' ',node[1])
                    direction[(node[0]-1,node[1])] = 'u'
                # down
                if([node[0]+1,node[1]] not in visit and node[0]+1 < 16 and vertical_wall[node[0]+1][node[1]] != 1):
                    visit.append([node[0]+1,node[1]])
                    queue.append([node[0]+1,node[1]])
                    # print('from',node[0],' ',node[1])
                    # print('to',node[0]+1,' ',node[1])
                    direction[(node[0]+1,node[1])] = 'd'
            distance += 1


def getStep(playerStat, ghostStat, propsStat):
    global action

    
    '''
    control of your player
    0: left, 1:right, 2: up, 3: down 4:no control
    format is (control, set landmine or not) = (0~3, True or False)
    put your control in action and time limit is 0.04sec for one step
    '''
    move = random.choice([0, 1, 2, 3, 4])
    landmine = False
    if playerStat[2] > 0:
        # landmine = random.choice([True, False])
        landmine = True
    action = [2, landmine]
    F_of_n = []
    props_direction = []
    
    for prop in propsStat:
        P_start_x = int(playerStat[0]/25)
        P_start_y = int(playerStat[1]/25)
        end_x = int(prop[1]/25)
        end_y = int(prop[2]/25)
        dis,dir = G_of_n([P_start_x,P_start_y],[end_x,end_y])
        F_of_n.append(dis + H_of_n([P_start_x,P_start_y],[end_x,end_y]))
        props_direction.append(dir)
    

# props img size => pellet = 5*5, landmine = 11*11, bomb = 11*11
# player, ghost img size=23x23


if __name__ == "__main__":
    # parallel_wall = zeros([16, 17])
    # vertical_wall = zeros([17, 16])
    (stop_program, id_package, parallel_wall, vertical_wall) = STcpClient.GetMap()

    
    while True:
        # playerStat: [x, y, n_landmine,super_time, score]
        # otherplayerStat: [x, y, n_landmine, super_time]
        # ghostStat: [[x, y],[x, y],[x, y],[x, y]]
        # propsStat: [[type, x, y] * N]
        (stop_program, id_package, playerStat,otherPlayerStat, ghostStat, propsStat) = STcpClient.GetGameStat()
        if stop_program:
            break
        elif stop_program is None:
            break
        global action
        action = None
        
        user_thread = MyThread(target=getStep, args=(playerStat, ghostStat, propsStat))
        user_thread.start()
        time.sleep(4/100)
        if action == None:
            user_thread.kill()
            user_thread.join()
            action = [4, False]
        is_connect=STcpClient.SendStep(id_package, action[0], action[1])
        if not is_connect:
            break
