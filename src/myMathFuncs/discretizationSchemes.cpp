#include "discretizationSchemes.h"

double forwardDiffFO(const double& currentVal, const double& nextVal, double dH){
    return (nextVal - currentVal)/(dH);
}

double backwardDiffFO(const double& currentVal, const double& previousVal, double dH)
{
    return (currentVal - previousVal)/(dH);
}

double centralDiffFO(const double& previousVal, const double& nextVal, double dH)
{
    return (nextVal - previousVal)/(2*dH);
}

double centralDiffSO(
    const double& currentVal, const double& previousVal,
    const double& nextVal, double dH
)
{
    return (nextVal - (2*currentVal) + previousVal)/(dH * dH);
}