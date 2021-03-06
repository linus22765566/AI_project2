
#include "STcpClient.h"
#include <stdlib.h>
#include <iostream>
#include <vector>
#include <thread>
#include <windows.h>

std::vector<int> step;

class Mythread
{
public:
	bool killed = false;
	/*
	輪到此程式移動

	change Step
	Step : vector, Step = {dir, is_throwLandmine}
			dir= 0: left, 1:right, 2: up, 3: down 4:do nothing
			is_throwLandmine= True/False
	*/
	void GetStep(int playerStat[4], int ghostStat[4][2], std::vector<std::vector<int>> propsStat)
	{
		// Example:
		unsigned seed;
		seed = (unsigned)time(NULL);
		srand(seed);
		int temp_step[2] = {0};
		// direction
		temp_step[0] = rand() % (5);
		// is_throwLandmine
		temp_step[1] = 0;
		if (playerStat[2] > 0)
		{
			temp_step[1] = rand() % 2;
		}
		if (killed == false)
		{
			step.resize(2);
			step[0] = temp_step[0];
			step[1] = temp_step[1];
		}
		delete this;
	}

	Mythread(int playerStat[4], int ghostStat[4][2], std::vector<std::vector<int>> propsStat)
	{
		std::thread t2(&Mythread::GetStep, this, playerStat, ghostStat, propsStat);
		t2.detach();
	}
};

int main()
{
	int id_package;
	/*
	playerStat: <x,y,n_landmine,super_time,score>
	otherPlayerStat: 3*<x,y,n_landmine,super_time>
	ghostStat: 4*<[x,y],[x,y],[x,y],[x,y]>
	propsStat: n_props*<type,x,y>
	*/
	int parallel_wall[16][17];
	int vertical_wall[17][16];
	int playerStat[5];
	int otherPlayerStat[3][5];
	int ghostStat[4][2];
	std::vector<std::vector<int>> propsStat;
	// receive map
	if (GetMap(parallel_wall, vertical_wall))
	{
		// start game
		while (true)
		{
			if (GetGameStat(id_package, playerStat, otherPlayerStat, ghostStat, propsStat))
				break;
			step.resize(2);
			step[0] = 5;
			step[1] = 2;
			Mythread *mythread = new Mythread(playerStat, ghostStat, propsStat);
			Sleep(40);
			if (step[0] == 5)
			{
				std::cout << "timeout" << std::endl;
				mythread->killed = true;
				step[0] = 4;
				step[1] = 0;
			}
			SendStep(id_package, step);
		}
	}
}
