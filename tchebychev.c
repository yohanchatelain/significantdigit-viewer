#include <assert.h>
#include <float.h>
#include <stdio.h>
#include <stdlib.h>

float coefs[] = {-200.,    6600.,     -84480.,  549120.,   -2050048.,
                 4659200., -6553600., 5570560., -2621440., 524288.};

int main(int argc, char **argv) {
  assert(argc == 2);
  float z = atof(argv[1]);

  float r = 1.0;

  float z2 = z * z;

  float p = z2;

  for (int i = 0; i < 10; i++) {
    r += coefs[i] * p;
    p *= z2;
  }

  printf("%.17e %.17e\n", z, r);
}
