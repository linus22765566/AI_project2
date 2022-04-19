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


def BFS_Player(start,prop_coo):
    # start = [8,8]
    queue = []

    global direction
    direction = {}
    direction[(start[0],start[1])] = 'none'
    queue.append(start)
    #print('Player is now',start,' to do BFS')
    level = 0
    while(len(queue)!= 0 ):
        node = queue.pop(0)
        # if(level >10):
        #     break
        # else:
        #     print('now is level',level)
        # print('現在BFS到',node)
        if((node[0],node[1]) in prop_coo):
            # do backtrace
            now_point_x = node[0]
            now_point_y = node[1]
            first_action = ''
            distance = 0
            print('pellet應該在',node,'玩家在',start)
            while((now_point_x!=start[0] or now_point_y !=start[1])):
                # print((now_point_x,now_point_y),'\'s direction is',direction[(now_point_x,now_point_y)])
                if(direction[(now_point_x,now_point_y)] == 'right'):
                    now_point_x -= 1
                    first_action = 'right'
                elif(direction[(now_point_x,now_point_y)] == 'left'):
                    now_point_x += 1
                    first_action = 'left'
                elif(direction[(now_point_x,now_point_y)] == 'up'):
                    now_point_y += 1
                    first_action = 'up'
                elif(direction[(now_point_x,now_point_y)] == 'down'):
                    now_point_y -= 1
                    first_action = 'down'
                distance += 1
            # if((first_action == 'up' or first_action == 'down') and (parallel_wall[now_point_x][now_point_y] == 1 or parallel_wall[now_point_x][now_point_y+1] == 1)):
            #     first_action == random.choice(['left','right'])
            # elif((first_action == 'right' or first_action == 'left')and (vertical_wall[now_point_x][now_point_y] == 1 or vertical_wall[now_point_x+1][now_point_y] == 1 )):
            #     first_action == random.choice(['up','down'])  
            return distance,first_action, node 
        # left
        if(((node[0]-1,node[1]) not in direction) and (vertical_wall[node[0]-1][node[1]] != 1.0)):
            # visit.append([node[0],node[1]-1])
            queue.append([node[0]-1,node[1]])
            # print('queue插入',[node[0],node[1]-1])
            # print('他的方向是 left\n')
            direction[(node[0]-1,node[1])] = 'left'
        # right
        if(((node[0]+1,node[1]) not in direction) and (vertical_wall[node[0]+1][node[1]] != 1.0)):
            # visit.append([node[0],node[1]+1])
            queue.append([node[0]+1,node[1]])
            # print('queue插入',[node[0],node[1]+1])
            # print('他的方向是 right\n')
            direction[(node[0]+1,node[1])] = 'right'
        # up
        if(((node[0],node[1]-1) not in direction) and (parallel_wall[node[0]][node[1]-1] != 1.0)):
            # visit.append([node[0]-1,node[1]])
            queue.append([node[0],node[1]-1])
            # print('queue插入',[node[0]-1,node[1]])
            # print('他的方向是 up\n')
            direction[(node[0],node[1]-1)] = 'up'
        # down
        if(((node[0],node[1]+1) not in direction) and (parallel_wall[node[0]][node[1]+1] != 1.0)):
            # visit.append([node[0]+1,node[1]])
            queue.append([node[0],node[1]+1])
            # print('queue插入',[node[0]+1,node[1]])
            # print('他的方向是 down\n')
            direction[(node[0],node[1]+1)] = 'down'





def getStep(playerStat, ghostStat, propsStat):
    global action
    actionlist = {'left':0,'right':1,'up':2,'down':3}
    actionlist2 ={0: "left", 1:"right", 2: "up", 3: "down"}
    '''
    control of your player
    0: left, 1:right, 2: up, 3: down 4:no control
    format is (control, set landmine or not) = (0~3, True or False)
    put your control in action and time limit is 0.04sec for one step
    '''
    move = random.choice([0, 1, 2, 3])
    landmine = False
    if playerStat[2] > 0:
        # landmine = random.choice([True, False])
        landmine = True
    P_start_x = int(playerStat[0]/25)
    P_start_y = int(playerStat[1]/25)
    props_cooridinates = []

    for prop in propsStat:
        if(prop[0] == 2):
            props_cooridinates.append((int(prop[1]/25),int(prop[2]/25)))
    dis , dir , toward= BFS_Player([P_start_x,P_start_y],props_cooridinates)
    print('now toward:',toward)
    print('now direction:',dir)
    print('now distance:',dis)
    print()
    action = [actionlist[dir], landmine]
    

    
    

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
        