#include "mpi.h"
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>
#include <string.h>
#include <papi.h> 
#include <math.h>

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
	#define OMEGA 5
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



//2200

#ifndef VECTOR_NUM
	#define VECTOR_NUM 14
#endif

#define CHUNK 5000
#define MSG_NUM BYTES_MSG/CHUNK

#define NR_PROCESSOS 3
 
#define NUMEVENTS 4
//#define MBYTES_MAXIMO_MEM MBYTES_MAXIMO - (BYTES_MSG*2/1024)
//#define VECTOR_SIZE (MBYTES*1024*1024)/8
//#define VECTOR_SIZE MBYTES_MAXIMO/VECTOR_NUM+1
#define SIZE_MSG BYTES_MSG




static const char *ErrMsg[] = {
  "Example program",
  "Couldn't find any hardware counters",
  "Couldn't start counting events",
  "Couldn't stop counting events",
  "Couldn't translate event code into event name"
};


static int Events[] = {
	PAPI_L3_TCA,
	PAPI_L3_TCM,
	PAPI_L2_TCA,
	PAPI_L2_TCM
	//PAPI_LD_INS,
	//PAPI_SR_INS
};




	

static long_long values[NUMEVENTS];
extern double mysecond();
char smsgbuf[SIZE_MSG];
char rmsgbuf[SIZE_MSG];


void handle_error(int errcode)
{
  	printf("Execution yielded error code %d : %s\n", errcode, ErrMsg[errcode]);
	exit(errcode);
}

void imprimir_resultado_memoria(double time, int passo_scalar, unsigned long int VECTOR_SIZE)
{
	unsigned long int iteracoes = VECTOR_SIZE/passo_scalar; 
	unsigned long int iteracoes_total = iteracoes * ALPHA;
//	unsigned long int iteracoes_total = VECTOR_SIZE*ALPHA; 
	

//	int bytes_por_iteracao = (VECTOR_NUM*8)+8;
	int bytes_por_iteracao = (VECTOR_NUM*8);
//	int bytes_por_iteracao = (VECTOR_NUM*2)+2;  
	

	float refs = (float)values[0];
	float misses = (float)values[1];
	
	float refsl2 = (float)values[2];
	float missesl2 = (float)values[3];
	
	float miss_rate = (misses/refs);
	float miss_ratel2 = (missesl2/refsl2);

	int rank;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);


//	printf("Taxa de acesso à DRAM: %.2f MB/s\n",(((bytes_por_iteracao*iteracoes_total)/1024/1024)/time));

	printf("[%d] Ref. L3 por segundo: %.2f \n",rank,(float)(values[0]/time)/1000/1000);
	printf("[%d] Ref. DRAM por segundo: %.2f \n",rank,(float)(values[1]/time)/1000/1000);
	printf("[%d] L3 Miss Rate: %.2f%% \n",rank,(float)miss_rate*100);
	//printf("L3 Hit Rate: %.2f%% \n",(float)(1-miss_rate)*100);
	//printf("Ref. L2 por segundo: %.2f \n",(float)(values[2]/time)/1000);
	//printf("Faltas L2 por segundo: %.2f \n",(float)(values[3]/time)/1000);
	//printf("L2 Hit Rate: %.2f%% \n",(float)(1-miss_ratel2)*100);
	//printf("L2 Miss Rate: %.2f%% \n",(float)miss_ratel2*100);


//	printf("Acessos total por segundo: %.2f \n",(float)((values[2]+values[3])/time)/1000);
	

}

void imprimir_resultado_rede(double time)
{
	//unsigned long int taxa = ((MBYTES*ALPHA*2));
	unsigned long int bytes = (unsigned long int) BYTES_MSG;
	unsigned long int beta = (unsigned long int) BETA;
	unsigned long int total_bytes = bytes*beta;
	total_bytes = (total_bytes)/1024/1024;
	double taxa = total_bytes/time;
		
	int rank;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);

	//printf("BYTES: %d \n", BYTES);
	printf("[%d] Taxa enviado: %2.f KB/s\n", rank, taxa);
}	

void print_results()
{ 
	char eventName[PAPI_MAX_STR_LEN];
  	int i;

  	for(i = 0; i < NUMEVENTS; i++) 
	{
    		if (PAPI_event_code_to_name(Events[i], eventName) != PAPI_OK)
      			handle_error(4);
    		//printf("Event %s: %lu\n", eventName, values[i]);
  	}

}


int fase_computacao(double **mat, double *passo, unsigned short int *passo_short, unsigned long int VECTOR_SIZE, int passo_scalar, int rank)
{
	int i,j,l,k;
	double tempo, tempo_inicial, tempo_final;
	double tempo_iteracao;
	//register double c1=500;
	//register double c2=400;
	//register double c3=300;
	//register double c4=500;
	//register double c5=400;
	//register double c6=300;
	
	//register double c1=rand();
	//register double c2=rand();
	//register double c3=rand();
	
	//double a[TETA];
	//double b[TETA];
	double a = rand();
	
	
	
	int x;
	
	
	//printf("Computando\n");
	
	if (PAPI_start_counters(Events, NUMEVENTS) != PAPI_OK) 
    		handle_error(2);

	tempo = mysecond();
	
	for(i=0;i<=ALPHA;i++)
	{
		//tempo_iteracao = mysecond();
		j=0;
		while(j<VECTOR_SIZE)
		{
			

			
			for(l=0;l<VECTOR_NUM;l+=3)
			{
				mat[l+1][j] = mat[l][j] + mat[l+2][j];
//				mat[l+1][j] = mat[l][j];
			
			}

			j += passo_scalar;
			for(k=0;k<TETA;k++)
				a = sqrt(a);
				
			//a = rand();
			//a = rand();
			//a = rand();
			//j = j + passo[j];
			
//			j = j + passo[j];
//			mat[l][j] = a;
			
//			j++;
			
			

			//asm("divsd   %xmm1, %xmm0");
			/*
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			asm("divsd   %xmm1, %xmm0");
			*/
			//j = j + x;
			//printf("%d\n",j);
			
			//mat[0][j] = j;
			//j++;
		
		}
		//printf("tempo por iteracao memoria: %f\n",mysecond()-tempo_iteracao);
		
	}
	

	tempo = mysecond()-tempo;	
	
	if (PAPI_stop_counters(values, NUMEVENTS) != PAPI_OK)
		handle_error(3);

	//if (rank == 0)
		imprimir_resultado_memoria(tempo,passo_scalar,VECTOR_SIZE);
	
}


int fase_comunicacao(int elementos, int rank)
{
	int  numtasks, rc, namelength, tag=1, dest, src;	
	int i,j;
	double tempo;
	double tempo_iteracao;
	
	
	//printf("Comunicando\n");

	tempo = mysecond();
	for(i=0;i<BETA;i++)
	{
		//tempo_iteracao = mysecond();
		MPI_Alltoall(smsgbuf,elementos,MPI_CHAR,rmsgbuf,elementos,MPI_CHAR,MPI_COMM_WORLD);
		//printf("tempo iteracao rede: %f\n",mysecond() - tempo_iteracao);
		//MPI_Alltoall(smsgbuf,10000,MPI_CHAR,rmsgbuf,10000,MPI_CHAR,MPI_COMM_WORLD);
		//for(j=0;j<MSG_NUM;j++)
		//MPI_Bcast(smsgbuf,SIZE_MSG,MPI_CHAR,0,MPI_COMM_WORLD);
	}

	
	tempo = mysecond()-tempo;
	
	//if(rank == 0)
		imprimir_resultado_rede(tempo);
	

}


int inicia_ambiente_mpi(int argc, char *argv[], int *rank, int *numtasks, int *elementos)
{
	int aux;
	MPI_Init(&argc,&argv);

	MPI_Comm_rank(MPI_COMM_WORLD, rank);
	MPI_Comm_size(MPI_COMM_WORLD, numtasks);
	aux = *numtasks;
	*elementos = SIZE_MSG/aux;

}


int finaliza_ambiente_mpi()
{
	MPI_Finalize();
}

void preparar_dados(char *smsgbuf, double *passo, unsigned short int *passo_short, int passo_scalar, double **mat, unsigned long int VECTOR_SIZE)
{
	int i,j;

	
	//for(i=0;i<VECTOR_SIZE;i++)
	  //     	passo[i] = passo_scalar;
	
	
	for(i=0;i<VECTOR_NUM;i++)
	{
		for(j=0;j<=VECTOR_SIZE;j++)
			mat[i][j] = passo_scalar;
	}



	for(i=0;i<SIZE_MSG;i++)
		smsgbuf[i] = (char)i;
	
	
}



int main (int argc, char *argv[])
{
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


	
	//passo_scalar = 1024/sizeof(double);
	passo_scalar = PASSO/sizeof(double);

//	VECTOR_SIZE = ((MBYTES_MAXIMO/(VECTOR_NUM+1))*1024); 
//	VECTOR_SIZE = (VECTOR_SIZE*1024)/8;

	
	VECTOR_SIZE =  ((BASE*WSS)/(NR_PROCESSOS*VECTOR_NUM))/sizeof(double);
	//VECTOR_SIZE = 1000;
	
	

//	printf("%f \n",(float)((VECTOR_SIZE*8)/1024/1024)*3); 
//	printf("WSS: %f \n",);
	printf("VECTOR_SIZE: %lu \n",(VECTOR_SIZE));


//	result = posix_memalign(&buffer,128, VECTOR_SIZE*8);
//	passo = (double*) buffer;	
	
	//passo_short = malloc(sizeof(unsigned short int)*VECTOR_SIZE);



	if(VECTOR_NUM != 0)
	{
		
		mat = (double**)malloc(sizeof(double*)*VECTOR_NUM);
		

		for(i=0;i<VECTOR_NUM;i++)
		{
			//buffer = aligned_alloc (32, VECTOR_SIZE*8);
			//mat[i] = (double*) malloc(sizeof(double)*VECTOR_SIZE);
			result = posix_memalign(&buffer,64, VECTOR_SIZE*8);
			mat[i] = (double*) buffer;
		}
	}

	


	if ((num_hwcntrs = PAPI_num_counters()) <= PAPI_OK)   
    		handle_error(1);

	//preparar_dados(smsgbuf,passo,passo_scalar,mat,VECTOR_SIZE);
	preparar_dados(smsgbuf,passo,passo_short,passo_scalar,mat,VECTOR_SIZE);
	inicia_ambiente_mpi(argc, argv, &rank, &numtasks, &elementos);

	

	time = mysecond();
	

	
	for(i=0;i<OMEGA;i++)
	{
		//printf("Computando...\n");
		tempo_comp = mysecond();
		fase_computacao(mat,passo,passo_short,VECTOR_SIZE,passo_scalar,rank);
		if(rank == 0)
			printf("computacao: %f\n",mysecond() - tempo_comp);

		//printf("Comunicando...\n");
		tempo_comum = mysecond();
		fase_comunicacao(elementos,rank);


		if(rank == 0)
		{
			printf("comunicacao: %f\n",mysecond() - tempo_comum);
			printf("Iteracao: %d\n",i);
		}

	}
	if(rank == 0)
		printf("Label: %d Tempo: %f - VectorNum: %d - %d\n", LABEL, mysecond()-time, VECTOR_NUM, BYTES_MSG);
	

	
	


	finaliza_ambiente_mpi();
	
}

#include <sys/time.h>

double mysecond()
{
        struct timeval tp;
        struct timezone tzp;
        int i;

        i = gettimeofday(&tp,&tzp);
        return ( (double) tp.tv_sec + (double) tp.tv_usec * 1.e-6 );
}

