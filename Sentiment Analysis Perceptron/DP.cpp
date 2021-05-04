// A Dynamic Programming based solution to find min cost
// to reach station N-1 from station 0.
#include<iostream>
#include<climits>
using namespace std;

#define INF INT_MAX
#define N 5

int min(int a,int b) {
    if (a >b) return a;
    else return b;
}
int minCost(int cost[][N])
{
        int OPT[N][N] = {0};
        OPT[N-1][N-1] = 0;
        int temp = 0;
        int MIN;

        for (int i=N-2; i>=0; i--) {
           MIN = INF;
           for (int j=i+1; j<=N-1; j++) {
              temp = min(cost[i][j], cost[i][j] + OPT[j][N-1]);
              if (temp < MIN) MIN = temp ;
           }
           OPT[i][N-1] = MIN;
        }
        return OPT[0][N-1];
}


void f1(int n) {
    int count = 0;
    for (int i=n/2;i<=n;i++){
        for (int k=1;k<=n;k=k*2) {
            for (int j=1;j<=n;j=j*2) {
                count++;
            }
        }
          

    }
    cout << count;
}

// Driver program to test above function
int main()
{
    f1(50);
    return 0;
}
