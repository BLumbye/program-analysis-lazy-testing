package jpamb.cases;

import utils.*;
import jpamb.utils.Case;
import jpamb.utils.Tag;
import static jpamb.utils.Tag.TagType.*;

public class Calls {

  public static void assertTrue() {
    assert true;
  }

  public static void assertFalse() {
    assert false;
  }

  public static void assertIf(boolean test) {
    if (test) {
      assertTrue();
    } else {
      assertFalse();
    }
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void callsAssertTrue() {
    assertTrue();
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ CALL })
  public static void callsAssertFalse() {
    assertFalse();
  }

  @Tag({ CALL })
  public static void callsAssertIf(boolean b) {
    assertIf(b);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void callsAssertIf_true() {
    assertIf(true);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void callsAssertIf_false() {
    assertIf(false);
  }

  public static int fib(int i) {
    if (i == 0 || i == 1)
      return i;
    return fib(i - 1) + fib(i - 2);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ CALL })
  public static void callsAssertIfWithTrue() {
    assertIf(true);
  }

  @Tag({ CALL, RECURSION })
  public static void callsAssertFib(int i) {
    assert fib(i) == 21;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void callsAssertFib_8() {
    assert fib(8) == 21;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void callsAssertFib_0() {
    assert fib(0) == 21;
  }

  public static int[] generatePrimeArray(int length) {
    assert length >= 0;
    int[] primeArray = new int[length];
    primeArray[0] = 2;
    int count = 1, number = 3;

    while (count < length) {
      boolean isprime = true;
      for (int p : primeArray) {
        isprime = number % p != 0;
        if (!isprime || p * p > number) {
          break;
        }
      }
      if (isprime) {
        primeArray[count] = number;
        count++;
      }
      number++;
    }

    return primeArray;
  }

  @Tag({ CALL, ARRAY, LOOP, INTEGER_OVERFLOW })
  public static void allPrimesArePositive(int number) {
    for (int p : generatePrimeArray(number)) {
      assert p > 0;
    }
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void allPrimesArePositive_100() {
    for (int p : generatePrimeArray(100)) {
      assert p > 0;
    }
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void allPrimesArePositive_0() {
    for (int p : generatePrimeArray(0)) {
      assert p > 0;
    }
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void allPrimesArePositive_n1() {
    for (int p : generatePrimeArray(-1)) {
      assert p > 0;
    }
  }

}
