#include <fstream>
#include <ostream>
#include <iostream>
#include <cstdlib>
#include <string>
#include <tuple>
#include <chrono>
#include <algorithm>
#include <cmath>

#include <eigen3/Eigen/Dense>
#include "myMathFuncs/discretizationSchemes.h"
#include "myMathFuncs/operators.h"

void writeCsv(const std::string& filename, const Eigen::MatrixXd& field)
{
    std::ofstream output(filename);
    output << "row,column,value\n";

    for (int row = 0; row < field.rows(); ++row)
    {
        for (int column = 0; column < field.cols(); ++column)
        {
            output << row << ',' << column << ',' << field(row, column) << '\n';
        }
    }
}

void writeResidualNorms(
    const std::string& filename, int timestep,
    const Eigen::MatrixXd& residual, std::string writemode="new")
{
    std::ofstream output;
    if (writemode == "append") {
        output.open(filename, std::ios_base::app | std::ios_base::out);
    } else {
        output.open(filename);
        output << "timestep,l2_norm,infinity_norm\n";
    }

    const double l2Norm = std::sqrt(residual.array().square().sum());
    const double infinityNorm = residual.cwiseAbs().maxCoeff();
    output << timestep << ',' << l2Norm << ',' << infinityNorm << '\n';
}

Eigen::MatrixXd getSourceTermB(
    const Eigen::MatrixXd& u, const Eigen::MatrixXd& v,
    double nx, double ny, double rho, double dt, double dx, double dy)
{
    Eigen::MatrixXd b = Eigen::MatrixXd::Zero(ny, nx);
    for(int j = 1; j< ny - 1; ++j)
    {
        for (int i = 1; i< nx - 1; ++i)
        {
            // Calculate derivate terms
            double dudx = centralDiffFO(u(j,i-1), u(j,i+1), dx);  
            double dvdy = centralDiffFO(v(j-1,i), v(j+1,i), dy);  
            double dudy = centralDiffFO(u(j-1,i), u(j+1,i), dy);  
            double dvdx = centralDiffFO(v(j,i-1), v(j,i+1), dx);  

            b(j,i) = (rho)*( (1/dt)*(dudx + dvdy) - sqr(dudx) - 2*dudy*dvdx - sqr(dvdy) );
        }
    }
    return b;
}

void pressurePoisson(
    Eigen::MatrixXd& p, const Eigen::MatrixXd& b,
    double dx, double dy, double rho, int nit)
{
    // Pseudo-time step and get p
    for (int q=0; q<nit; ++q)
    {
        for(int j = 1; j< p.rows() - 1; ++j)
        {
            for (int i = 1; i<p.cols() - 1; ++i)
            {
                double pTerms = ((p(j,i+1) + p(j,i-1))/sqr(dx)) +(p(j+1,i)+p(j-1,i))/sqr(dy);

                p(j,i) = ( (b(j,i) - pTerms)/(-2.0) ) * ( (sqr(dx)*sqr(dy))/(sqr(dx)+sqr(dy)) );
            }
        }
        
        // Re-apply B.Cs
        p.col(p.cols() - 1) = p.col(p.cols() - 2);  // dp/dx = 0 at x = 2
        p.row(0) = p.row(1);                        // dp/dy = 0 at y = 0
        p.col(0) = p.col(1);                        // dp/dx = 0 at x = 0
        p.row(p.rows() - 1).setZero();                 // p = 0 at y = 2

    }
}

// tuple is the return type of the cavityFlow func
std::tuple<Eigen::MatrixXd, Eigen::MatrixXd, Eigen::MatrixXd> 
cavityFlow(
    Eigen::MatrixXd u, Eigen::MatrixXd v, Eigen::MatrixXd p,
    double nt, double nit, double cfl, double dx, double dy,
    double nx, double ny, double rho, double nu, double u_bc)
{
    for (int n=0; n<nt; ++n) 
    {   
        double u_max = u.cwiseAbs().maxCoeff();
        double v_max = v.cwiseAbs().maxCoeff();
        double epsilon = 1e-10;
        double convectiveDt = std::min(
            dx / (u_max + epsilon),
            dy / (v_max + epsilon));
        double diffusiveDt = sqr(dx)/(nu*4.0);
        double dt = cfl * std::min(convectiveDt, diffusiveDt);

        Eigen::MatrixXd un = u;
        Eigen::MatrixXd vn = v;

        Eigen::MatrixXd b = getSourceTermB(u, v, nx, ny, rho, dt, dx, dy);
        pressurePoisson(p, b, dx, dy, rho, nit);

        if (n % 50 == 0) {
            std::cout << "Timestep: " << n << '\n';
        }

        // Go through interior points
        for(int j = 1; j< ny - 1; ++j)
        {
            for (int i = 1; i<nx - 1; ++i)
            {
                // Build terms
                double dudx = upwindFO(un(j,i),un(j,i), un(j,i+1), un(j,i-1), dx);
                double dudy = upwindFO(vn(j,i),un(j,i), un(j+1,i), un(j-1,i), dy);
                double dpdx = centralDiffFO(p(j,i-1), p(j,i+1), dx);
                double d2udx2 = centralDiffSO(un(j,i), un(j,i-1), un(j,i+1), dx);
                double d2udy2 = centralDiffSO(un(j,i), un(j-1,i), un(j+1,i), dy);
                
                double dvdx = upwindFO(un(j,i), vn(j,i), vn(j,i+1), vn(j,i-1), dx);
                double dvdy = upwindFO(vn(j,i),vn(j,i), vn(j+1,i), vn(j-1,i), dy);
                double dpdy = centralDiffFO(p(j-1,i), p(j+1,i), dy);
                double d2vdx2 = centralDiffSO(vn(j,i), vn(j,i-1), vn(j,i+1), dx);
                double d2vdy2 = centralDiffSO(vn(j,i), vn(j-1,i), vn(j+1,i), dy);
                
                double convectionTermX = un(j,i)*dudx + vn(j,i)*dudy;
                double pressureTermX = (-1/rho)*dpdx;
                double diffusionTermX = (nu)*(d2udx2 + d2udy2);

                double convectionTermY = un(j,i)*dvdx + vn(j,i)*dvdy;
                double pressureTermY = (-1/rho)*dpdy;
                double diffusionTermY = (nu)*(d2vdx2 + d2vdy2);

                u(j,i) = un(j,i) + (dt)*(pressureTermX - convectionTermX + diffusionTermX);
                v(j,i) = vn(j,i) + (dt)*(pressureTermY - convectionTermY + diffusionTermY);
            }
        }

        // Re-apply B.Cs
        u.row(0).setZero();
        u.col(0).setZero();
        u.col(u.cols()-1).setZero();
        u.row(u.rows()-1).setConstant(u_bc);

        v.row(0).setZero();
        v.col(0).setZero();
        v.row(v.rows()-1).setZero();
        v.col(v.cols()-1).setZero();

        // Write out residuals for u,v
        // TODO - Can probably write out every 50 or so iterations, should speedup for large nt's
        Eigen::MatrixXd u_residual = (u - un)/dt;
        Eigen::MatrixXd v_residual = (v - vn)/dt;
        const std::string writeMode = (n == 0) ? "new" : "append";
        writeResidualNorms("../data/u_residual_norms.csv", n, u_residual, writeMode);
        writeResidualNorms("../data/v_residual_norms.csv", n, v_residual, writeMode);

    }
    return {u, v, p};
}

int main() 
{
    auto startTime = std::chrono::steady_clock::now();

    // User input var
    double u_bc = 100.0;    // U velocity boundary condition
    int nx_user = 129;
    int nt = 80000;
    int nit = 50;           // Pseudo-time variable used in pressure poisson equation
    double nu = 0.1;
    double rho = 0.1;
    double cfl = 0.5;       // Used in adaptive time step calc. Technically this should be called safety factor i think
    
    int nx = nx_user;
    double dx = 1.0 / (nx - 1.0);
    int ny = nx;
    double dy = dx;


    // Initialise matrices
    Eigen::MatrixXd u = Eigen::MatrixXd::Zero(ny, nx);
    u.row(0).setConstant(u_bc);

    Eigen::MatrixXd v = Eigen::MatrixXd::Zero(ny, nx);
    Eigen::MatrixXd p = Eigen::MatrixXd::Zero(ny, nx);
    Eigen::MatrixXd b = Eigen::MatrixXd::Zero(ny, nx);

    // Advance cavity flow solution
    // std::tie unpacks the tuple into u,v,p
    std::tie(u, v, p) = cavityFlow(u, v, p, nt, nit, cfl, dx, dy, nx, ny, rho, nu, u_bc);

    // Assuming exe is run from the build dir
    writeCsv("../data/u.csv", u);
    writeCsv("../data/v.csv", v);
    writeCsv("../data/p.csv", p);

    auto endTime = std::chrono::steady_clock::now();
    auto elapsed = std::chrono::duration<double>(endTime - startTime);

    std::cout << "Total execution time: "
            << elapsed.count() << " seconds\n";

    return 0;
}