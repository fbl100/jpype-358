package com.example.calculation;

import org.apache.commons.math3.complex.Complex;

import java.time.Duration;
import java.time.Instant;

public class Mandelbrot
{
    // return number of iterations to check if c = a + ib is in Mandelbrot set
    public static int mand(Complex z0, int max) {
        Complex z = z0;
        for (int t = 0; t < max; t++) {
            if (z.abs() > 2.0) return t;
            z = z.multiply(z).add(z0);
        }
        return max;
    }

    public static void main(String[] args)
    {
        Long millis = doMandelBrot(-0.5, 0);
        System.out.println(millis);
    }

    public static Long doMandelBrot(double xc, double yc)
    {

        double size = 2;

        int n   = 1024;   // create n-by-n image
        int max = 1024;   // maximum number of iterations

        Instant tStart = Instant.now();

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                double x0 = xc - size/2 + size*i/n;
                double y0 = yc - size/2 + size*j/n;
                Complex z0 = new Complex(x0, y0);
                int gray = max - mand(z0, max);
            }
        }

        Instant tEnd = Instant.now();
        Duration d = Duration.between(tStart, tEnd);
        return d.toMillis();
    }
}
