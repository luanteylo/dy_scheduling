#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>
#include <string.h>
#include <math.h>

/****************************************
Universidade Federal Fluminense (UFF)
Insituto de Computação
Niterói, Brazil
Authors: Maicon Melo Alves and Lucia Maria de Assumpcao Drummond
Description: synthetic application template able to create synthetic applications with distinct access profiles to SLLC, DRAM and network. 
Dependencies: MPI and PAPI
*****************************************/



#ifndef LABEL
	#define LABEL 0
#endif

#ifndef ALPHA
	#define ALPHA 700
#endif

#ifndef TETA
	#define TETA 0
#endif

#ifndef WSS
	#define WSS 0
#endif


#ifndef BETA
	#define BETA 100
#endif

#ifndef OMEGA
	#define OMEGA 25
#endif

#ifndef BYTES_MSG
	#define BYTES_MSG 10485760
#endif

#ifndef MBYTES_MAXIMO
	#define MBYTES_MAXIMO 3500
#endif

#ifndef MBYTES
	#define MBYTES 1
#endif

#ifndef PASSO
	#define PASSO 1
#endif


#ifndef VECTOR_NUM
	#define VECTOR_NUM 14
#endif

#define CHUNK 5000

#define MSG_NUM BYTES_MSG/CHUNK

#define NR_PROCESSOS 3

#define NUMEVENTS 4


#define SIZE_MSG BYTES_MSG


// static long_long values[NUMEVENTS];
extern double mysecond();
char smsgbuf[SIZE_MSG];
char rmsgbuf[SIZE_MSG];



void imprimir_resultado_rede(double time){
	//unsigned long int taxa = ((MBYTES*ALPHA*2));
	unsigned long int bytes = (unsigned long int) BYTES_MSG;
	unsigned long int beta = (unsigned long int) BETA;
	unsigned long int total_bytes = bytes*beta;
	total_bytes = (total_bytes)/1024/1024;
	double taxa = total_bytes/time;

	int rank;
	//MPI_Comm_rank(MPI_COMM_WORLD, &rank);

	
	//printf("[%d] Taxa enviado: %2.f KB/s\n", rank, taxa);
}	


int fase_computacao(double **mat, unsigned long int VECTOR_SIZE, int passo_scalar, int rank){
	int i,j,l,k;

	double tempo, tempo_inicial, tempo_final;
	double tempo_iteracao;
	
	double a = rand();
		
	
	int x;	
	
	tempo = mysecond();

	#pragma omp parallel 
	{
	printf("My id: %d\n", omp_get_thread_num());
		
	#pragma omp parallel for
	for(i = 0;i <= ALPHA; i++){
		//tempo_iteracao = mysecond();
		j = 0;
		while(j < VECTOR_SIZE){

			
			for(l = 0; l < VECTOR_NUM; l += 3) {
				mat[l+1][j] = mat[l][j] + mat[l+2][j];

			}

			j += passo_scalar;
			for( k = 0; k < TETA; k++)
				a = sqrt(a);

		}
		
	}
	
	tempo = mysecond()-tempo;	
	}
}

/*
int fase_comunicacao(int elementos, int rank){
	int  numtasks, rc, namelength, tag=1, dest, src;	
	int i,j;
	double tempo;
	double tempo_iteracao;
	
	
	//printf("Comunicando\n");

	tempo = mysecond();
	for(i=0;i<BETA;i++){
		MPI_Alltoall(smsgbuf, elementos, MPI_CHAR, rmsgbuf, elementos, MPI_CHAR, MPI_COMM_WORLD);
	}

	
	tempo = mysecond()-tempo;
	
	imprimir_resultado_rede(tempo);
}


int inicia_ambiente_mpi(int argc, char *argv[], int *rank, int *numtasks, int *elementos){
	int aux;
	MPI_Init(&argc,&argv);

	MPI_Comm_rank(MPI_COMM_WORLD, rank);
	MPI_Comm_size(MPI_COMM_WORLD, numtasks);
	aux = *numtasks;
	*elementos = SIZE_MSG/aux;
}


int finaliza_ambiente_mpi(){
	MPI_Finalize();
}
*/
void preparar_dados(char *smsgbuf, int passo_scalar, double **mat, unsigned long int VECTOR_SIZE){
	int i,j;


	for(i=0;i<VECTOR_NUM;i++){
		for(j=0;j<=VECTOR_SIZE;j++)
			mat[i][j] = passo_scalar;
	}

	for(i=0;i<SIZE_MSG;i++)
		smsgbuf[i] = (char)i;
		
}



int main (int argc, char *argv[]){
	// mpi vars
	int i;
	int rank, numtasks, elementos;

	double **mat;
	double *passo;
	unsigned short int *passo_short;
	unsigned long int VECTOR_SIZE;
	unsigned long int BASE=1024;
	
	int passo_scalar, j;
	double time;
	int num_hwcntrs;
	char **msg;
	double tempo_comp, tempo_comum;
	void *buffer;
	int result;

	


	
	passo_scalar = PASSO/sizeof(double);
	
	VECTOR_SIZE =  ((BASE*WSS)/(NR_PROCESSOS*VECTOR_NUM))/sizeof(double);

	printf("VECTOR_SIZE: %lu \n",(VECTOR_SIZE));

	if(VECTOR_NUM != 0){

		mat = (double**) malloc(sizeof(double*) * VECTOR_NUM);
		
		for(i = 0; i < VECTOR_NUM; i++){
			result = posix_memalign(&buffer, 64, VECTOR_SIZE*8);
			mat[i] = (double*) buffer;
		}
	}

	preparar_dados(smsgbuf, passo_scalar, mat, VECTOR_SIZE);
	//inicia_ambiente_mpi(argc, argv, &rank, &numtasks, &elementos);

	
	time = mysecond();
	
	for(i = 0; i < OMEGA; i++) {
		//printf("Computando...\n");
		tempo_comp = mysecond();
		printf("My id: %d\n, My Omega; %d\n", omp_get_thread_num(),i);
		//INICIO REGIÃO PARALELA
		fase_computacao(mat, VECTOR_SIZE,passo_scalar,rank);
		//TÉRMINO REGIÃO PARALELA


		//printf("computacao: %f\n",mysecond() - tempo_comp);

		//printf("Comunicando...\n");
		tempo_comum = mysecond();
		//fase_comunicacao(elementos,rank);


		/*if(rank == 0) {
			printf("comunicacao: %f\n",mysecond() - tempo_comum);
			printf("Iteracao: %d\n",i);
		}*/

	}

	
	
		printf("Label: %d Tempo: %f - VectorNum: %d - %d\n", LABEL, mysecond()-time, VECTOR_NUM, BYTES_MSG);
	
	//finaliza_ambiente_mpi();
	}


#include <sys/time.h>

double mysecond(){
	struct timeval tp;
	struct timezone tzp;
	int i;

	i = gettimeofday(&tp,&tzp);
	return ( (double) tp.tv_sec + (double) tp.tv_usec * 1.e-6 );
}
