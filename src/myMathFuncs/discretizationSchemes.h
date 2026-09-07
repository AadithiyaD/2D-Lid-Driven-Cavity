#pragma once

double forwardDiffFO(const double& currentVal, const double& nextVal, double dH);
double backwardDiffFO(const double& currentVal, const double& previousVal, double dH);
double centralDiffFO(const double& previousVal, const double& nextVal, double dH);
double centralDiffSO(
	const double& currentVal,
	const double& previousVal,
	const double& nextVal,
	double dH
);
double upwindFO(
	const double& advectingVelo,
    const double& currentVal,
    const double& nextVal,
    const double& previousVal,
    double dH
);