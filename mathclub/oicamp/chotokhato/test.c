#include <stdio.h>
int main() {
  // Say, input is : 10 power 1.2

  int first;
  char word[5];
  float second;

  scanf("%d %s %f", &first, word, &second); // You don't need & for arrays.

  printf("Integer : %d\nWord : %s\nFloat : %f\n", first, word, second);
  return 0;

}