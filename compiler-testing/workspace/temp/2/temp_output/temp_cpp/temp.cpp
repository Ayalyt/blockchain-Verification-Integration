#include <stdio.h>
#include <iostream>
#include <assert.h>
#include "circom.hpp"
#include "calcwit.hpp"
void aVARFsx6R1vP_0_create(uint soffset,uint coffset,Circom_CalcWit* ctx,std::string componentName,uint componentFather);
void aVARFsx6R1vP_0_run(uint ctx_index,Circom_CalcWit* ctx);
void nf0jPugYZl1I_1_create(uint soffset,uint coffset,Circom_CalcWit* ctx,std::string componentName,uint componentFather);
void nf0jPugYZl1I_1_run(uint ctx_index,Circom_CalcWit* ctx);
void get_one_0(Circom_CalcWit* ctx,FrElement* lvar,FrElement* destination,int destination_size);
Circom_TemplateFunction _functionTable[2] = { 
aVARFsx6R1vP_0_run,
nf0jPugYZl1I_1_run };
uint get_main_input_signal_start() {return 5;}

uint get_main_input_signal_no() {return 4;}

uint get_total_signal_no() {return 22;}

uint get_number_of_components() {return 2;}

uint get_size_of_input_hashmap() {return 256;}

uint get_size_of_witness() {return 17;}

uint get_size_of_constants() {return 43;}

uint get_size_of_io_map() {return 0;}

// function declarations
void get_one_0(Circom_CalcWit* ctx,FrElement* lvar,FrElement* destination,int destination_size){
FrElement* circuitConstants = ctx->circuitConstants;
FrElement expaux[1];
// return bucket
Fr_copy(destination,&circuitConstants[24]);
return;
}

// template declarations
void aVARFsx6R1vP_0_create(uint soffset,uint coffset,Circom_CalcWit* ctx,std::string componentName,uint componentFather){
ctx->componentMemory[coffset].templateId = 0;
ctx->componentMemory[coffset].templateName = "aVARFsx6R1vP";
ctx->componentMemory[coffset].signalStart = soffset;
ctx->componentMemory[coffset].inputCounter = 5;
ctx->componentMemory[coffset].componentName = componentName;
ctx->componentMemory[coffset].idFather = componentFather;
ctx->componentMemory[coffset].subcomponents = new uint[0];
}

void aVARFsx6R1vP_0_run(uint ctx_index,Circom_CalcWit* ctx){
FrElement* signalValues = ctx->signalValues;
u64 mySignalStart = ctx->componentMemory[ctx_index].signalStart;
std::string myTemplateName = ctx->componentMemory[ctx_index].templateName;
std::string myComponentName = ctx->componentMemory[ctx_index].componentName;
u64 myFather = ctx->componentMemory[ctx_index].idFather;
u64 myId = ctx_index;
u32* mySubcomponents = ctx->componentMemory[ctx_index].subcomponents;
FrElement* circuitConstants = ctx->circuitConstants;
std::string* listOfTemplateMessages = ctx->listOfTemplateMessages;
FrElement expaux[5];
FrElement lvar[31];
uint sub_component_aux;
{
PFrElement aux_dest = &lvar[0];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[0]);
}
{
PFrElement aux_dest = &lvar[1];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[1]);
}
{
PFrElement aux_dest = &lvar[2];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[2]);
}
{
PFrElement aux_dest = &lvar[3];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[3]);
}
{
PFrElement aux_dest = &lvar[4];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[4]);
}
{
PFrElement aux_dest = &lvar[5];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[5]);
}
{
PFrElement aux_dest = &lvar[6];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[6]);
}
{
PFrElement aux_dest = &lvar[7];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[7]);
}
{
PFrElement aux_dest = &lvar[8];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[8]);
}
{
PFrElement aux_dest = &lvar[9];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[9]);
}
{
PFrElement aux_dest = &lvar[10];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[10]);
}
{
PFrElement aux_dest = &lvar[11];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[11]);
}
{
PFrElement aux_dest = &lvar[12];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[12]);
}
{
PFrElement aux_dest = &lvar[13];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[13]);
}
{
PFrElement aux_dest = &lvar[14];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[14]);
}
{
PFrElement aux_dest = &lvar[15];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[15]);
}
{
PFrElement aux_dest = &lvar[16];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[16]);
}
{
PFrElement aux_dest = &lvar[17];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[1]);
}
{
PFrElement aux_dest = &lvar[18];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[17]);
}
{
PFrElement aux_dest = &lvar[19];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[18]);
}
{
PFrElement aux_dest = &lvar[20];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[19]);
}
{
PFrElement aux_dest = &lvar[21];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[4]);
}
{
PFrElement aux_dest = &lvar[22];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[20]);
}
{
PFrElement aux_dest = &lvar[23];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[21]);
}
{
PFrElement aux_dest = &lvar[24];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[22]);
}
{

// start of call bucket
FrElement lvarcall[0];
get_one_0(ctx,lvarcall,&lvar[25],1);
// end call bucket
}

{

// start of call bucket
FrElement lvarcall[0];
get_one_0(ctx,lvarcall,&lvar[26],1);
// end call bucket
}

{

// start of call bucket
FrElement lvarcall[0];
get_one_0(ctx,lvarcall,&lvar[27],1);
// end call bucket
}

{

// start of call bucket
FrElement lvarcall[0];
get_one_0(ctx,lvarcall,&lvar[28],1);
// end call bucket
}

{

// start of call bucket
FrElement lvarcall[0];
get_one_0(ctx,lvarcall,&lvar[29],1);
// end call bucket
}

Fr_leq(&expaux[0],&circuitConstants[23],&signalValues[mySignalStart + 7]); // line circom 139
if(Fr_isTrue(&expaux[0])){
{
PFrElement aux_dest = &lvar[30];
// load src
// end load src
Fr_copy(aux_dest,&lvar[(((3 * (Fr_toInt(&lvar[25]) * 2)) + (1 * (Fr_toInt(&lvar[26]) * 2))) + 12)]);
}
}else{
{
PFrElement aux_dest = &lvar[30];
// load src
Fr_shr(&expaux[0],&lvar[(((3 * (Fr_toInt(&lvar[27]) * 1)) + (1 * (Fr_toInt(&lvar[28]) * 2))) + 12)],&signalValues[mySignalStart + ((1 * (Fr_toInt(&lvar[29]) * 0)) + 6)]); // line circom 139
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
}
{
PFrElement aux_dest = &lvar[24];
// load src
Fr_shl(&expaux[0],&circuitConstants[22],&lvar[30]); // line circom 139
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
Fr_eq(&expaux[0],&signalValues[mySignalStart + 3],&signalValues[mySignalStart + 3]); // line circom 140
if (!Fr_isTrue(&expaux[0])) std::cout << "Failed assert in template " << myTemplateName << " line 140. " <<  "Followed trace: " << ctx->getTrace(myId) << std::endl;
assert(Fr_isTrue(&expaux[0]));
{
PFrElement aux_dest = &signalValues[mySignalStart + 2];
// load src
Fr_sub(&expaux[0],&signalValues[mySignalStart + 7],&signalValues[mySignalStart + 6]); // line circom 141
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
Fr_mul(&expaux[2],&circuitConstants[25],&signalValues[mySignalStart + 4]); // line circom 142
Fr_eq(&expaux[0],&signalValues[mySignalStart + 5],&expaux[2]); // line circom 142
if (!Fr_isTrue(&expaux[0])) std::cout << "Failed assert in template " << myTemplateName << " line 142. " <<  "Followed trace: " << ctx->getTrace(myId) << std::endl;
assert(Fr_isTrue(&expaux[0]));
{
PFrElement aux_dest = &signalValues[mySignalStart + 0];
// load src
Fr_mul(&expaux[0],&circuitConstants[23],&signalValues[mySignalStart + 5]); // line circom 143
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
{
PFrElement aux_dest = &signalValues[mySignalStart + 1];
// load src
Fr_add(&expaux[0],&signalValues[mySignalStart + 5],&signalValues[mySignalStart + 3]); // line circom 144
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
}

void nf0jPugYZl1I_1_create(uint soffset,uint coffset,Circom_CalcWit* ctx,std::string componentName,uint componentFather){
ctx->componentMemory[coffset].templateId = 1;
ctx->componentMemory[coffset].templateName = "nf0jPugYZl1I";
ctx->componentMemory[coffset].signalStart = soffset;
ctx->componentMemory[coffset].inputCounter = 4;
ctx->componentMemory[coffset].componentName = componentName;
ctx->componentMemory[coffset].idFather = componentFather;
ctx->componentMemory[coffset].subcomponents = new uint[1];
}

void nf0jPugYZl1I_1_run(uint ctx_index,Circom_CalcWit* ctx){
FrElement* signalValues = ctx->signalValues;
u64 mySignalStart = ctx->componentMemory[ctx_index].signalStart;
std::string myTemplateName = ctx->componentMemory[ctx_index].templateName;
std::string myComponentName = ctx->componentMemory[ctx_index].componentName;
u64 myFather = ctx->componentMemory[ctx_index].idFather;
u64 myId = ctx_index;
u32* mySubcomponents = ctx->componentMemory[ctx_index].subcomponents;
FrElement* circuitConstants = ctx->circuitConstants;
std::string* listOfTemplateMessages = ctx->listOfTemplateMessages;
FrElement expaux[6];
FrElement lvar[23];
uint sub_component_aux;
{
PFrElement aux_dest = &lvar[0];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[10]);
}
{
PFrElement aux_dest = &lvar[1];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[26]);
}
{
PFrElement aux_dest = &lvar[2];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[22]);
}
{
PFrElement aux_dest = &lvar[3];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[14]);
}
{
PFrElement aux_dest = &lvar[4];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[27]);
}
{
PFrElement aux_dest = &lvar[5];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[28]);
}
{
PFrElement aux_dest = &lvar[6];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[29]);
}
{
PFrElement aux_dest = &lvar[7];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[12]);
}
{
PFrElement aux_dest = &lvar[8];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[22]);
}
{
PFrElement aux_dest = &lvar[9];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[1]);
}
{
PFrElement aux_dest = &lvar[10];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[30]);
}
{
PFrElement aux_dest = &lvar[11];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[31]);
}
{
PFrElement aux_dest = &lvar[12];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[7]);
}
{
PFrElement aux_dest = &lvar[13];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[32]);
}
{
PFrElement aux_dest = &lvar[14];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[30]);
}
{
PFrElement aux_dest = &lvar[15];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[33]);
}
{
PFrElement aux_dest = &lvar[16];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[34]);
}
{
uint aux_create = 0;
int aux_cmp_num = 0+ctx_index+1;
uint csoffset = mySignalStart+11;
for (uint i = 0; i < 1; i++) {
std::string new_cmp_name = "YOKD7N8ElVIL";
mySubcomponents[aux_create+i] = aux_cmp_num;
aVARFsx6R1vP_0_create(csoffset,aux_cmp_num,ctx,new_cmp_name,myId);
csoffset += 10 ;
aux_cmp_num += 1;
}
}
{
PFrElement aux_dest = &lvar[18];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[35]);
}
Fr_gt(&expaux[0],&lvar[18],&circuitConstants[23]); // line circom 211
while(Fr_isTrue(&expaux[0])){
{
PFrElement aux_dest = &lvar[17];
// load src
Fr_mul(&expaux[0],&lvar[17],&circuitConstants[14]); // line circom 212
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
{
PFrElement aux_dest = &lvar[17];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[36]);
}
{

// start of call bucket
FrElement lvarcall[0];
get_one_0(ctx,lvarcall,&lvar[19],1);
// end call bucket
}

{

// start of call bucket
FrElement lvarcall[0];
get_one_0(ctx,lvarcall,&lvar[20],1);
// end call bucket
}

{

// start of call bucket
FrElement lvarcall[0];
get_one_0(ctx,lvarcall,&lvar[21],1);
// end call bucket
}

{

// start of call bucket
FrElement lvarcall[0];
get_one_0(ctx,lvarcall,&lvar[22],1);
// end call bucket
}

Fr_leq(&expaux[0],&circuitConstants[24],&signalValues[mySignalStart + 4]); // line circom 214
if(Fr_isTrue(&expaux[0])){
{
PFrElement aux_dest = &lvar[17];
// load src
Fr_mul(&expaux[0],&lvar[(((4 * (Fr_toInt(&lvar[19]) * 1)) + (1 * (Fr_toInt(&lvar[20]) * 0))) + 0)],&signalValues[mySignalStart + (((1 * (Fr_toInt(&lvar[21]) * 0)) + (1 * (Fr_toInt(&lvar[22]) * 0))) + 7)]); // line circom 214
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
}else{
{
PFrElement aux_dest = &lvar[17];
// load src
Fr_bnot(&expaux[2],&signalValues[mySignalStart + 5]); // line circom 214
Fr_add(&expaux[1],&expaux[2],&circuitConstants[23]); // line circom 214
Fr_band(&expaux[0],&expaux[1],&circuitConstants[23]); // line circom 214
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
}
{
PFrElement aux_dest = &lvar[17];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[37]);
}
{
PFrElement aux_dest = &lvar[17];
// load src
// end load src
Fr_copy(aux_dest,&circuitConstants[38]);
}
{
PFrElement aux_dest = &lvar[18];
// load src
Fr_sub(&expaux[0],&lvar[18],&circuitConstants[24]); // line circom 217
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
Fr_gt(&expaux[0],&lvar[18],&circuitConstants[23]); // line circom 211
}
{
PFrElement aux_dest = &signalValues[mySignalStart + 0];
// load src
Fr_sub(&expaux[0],&signalValues[mySignalStart + 6],&signalValues[mySignalStart + 6]); // line circom 219
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
{
PFrElement aux_dest = &signalValues[mySignalStart + 1];
// load src
Fr_sub(&expaux[2],&signalValues[mySignalStart + 5],&signalValues[mySignalStart + 5]); // line circom 220
Fr_mul(&expaux[0],&circuitConstants[39],&expaux[2]); // line circom 220
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
{
PFrElement aux_dest = &signalValues[mySignalStart + 2];
// load src
Fr_sub(&expaux[0],&signalValues[mySignalStart + 7],&signalValues[mySignalStart + 7]); // line circom 221
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
{
PFrElement aux_dest = &signalValues[mySignalStart + 3];
// load src
// end load src
Fr_copy(aux_dest,&signalValues[mySignalStart + 6]);
}
{
uint cmp_index_ref = 0;
{
PFrElement aux_dest = &ctx->signalValues[ctx->componentMemory[mySubcomponents[cmp_index_ref]].signalStart + 3];
// load src
Fr_mul(&expaux[1],&signalValues[mySignalStart + 7],&circuitConstants[40]); // line circom 223
Fr_sub(&expaux[0],&expaux[1],&signalValues[mySignalStart + 5]); // line circom 223
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
// no need to run sub component
assert(--ctx->componentMemory[mySubcomponents[cmp_index_ref]].inputCounter);
}
{
uint cmp_index_ref = 0;
{
PFrElement aux_dest = &ctx->signalValues[ctx->componentMemory[mySubcomponents[cmp_index_ref]].signalStart + 4];
// load src
Fr_sub(&expaux[3],&signalValues[mySignalStart + 4],&signalValues[mySignalStart + 6]); // line circom 224
Fr_add(&expaux[2],&expaux[3],&signalValues[mySignalStart + 7]); // line circom 224
Fr_mul(&expaux[0],&circuitConstants[41],&expaux[2]); // line circom 224
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
// no need to run sub component
assert(--ctx->componentMemory[mySubcomponents[cmp_index_ref]].inputCounter);
}
{
uint cmp_index_ref = 0;
{
PFrElement aux_dest = &ctx->signalValues[ctx->componentMemory[mySubcomponents[cmp_index_ref]].signalStart + 5];
// load src
Fr_mul(&expaux[0],&circuitConstants[4],&signalValues[mySignalStart + 5]); // line circom 225
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
// no need to run sub component
assert(--ctx->componentMemory[mySubcomponents[cmp_index_ref]].inputCounter);
}
{
uint cmp_index_ref = 0;
{
PFrElement aux_dest = &ctx->signalValues[ctx->componentMemory[mySubcomponents[cmp_index_ref]].signalStart + 6];
// load src
Fr_sub(&expaux[1],&signalValues[mySignalStart + 6],&signalValues[mySignalStart + 6]); // line circom 226
Fr_sub(&expaux[0],&expaux[1],&signalValues[mySignalStart + 6]); // line circom 226
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
// no need to run sub component
assert(--ctx->componentMemory[mySubcomponents[cmp_index_ref]].inputCounter);
}
{
uint cmp_index_ref = 0;
{
PFrElement aux_dest = &ctx->signalValues[ctx->componentMemory[mySubcomponents[cmp_index_ref]].signalStart + 7];
// load src
Fr_mul(&expaux[0],&signalValues[mySignalStart + 6],&circuitConstants[42]); // line circom 227
// end load src
Fr_copy(aux_dest,&expaux[0]);
}
// need to run sub component
assert(!(--ctx->componentMemory[mySubcomponents[cmp_index_ref]].inputCounter));
aVARFsx6R1vP_0_run(mySubcomponents[cmp_index_ref],ctx);
}
}

void run(Circom_CalcWit* ctx){
nf0jPugYZl1I_1_create(1,0,ctx,"main",0);
nf0jPugYZl1I_1_run(0,ctx);
}

