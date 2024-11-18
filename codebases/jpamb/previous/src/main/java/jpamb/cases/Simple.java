package jpamb.cases;

import utils.*;
import jpamb.utils.Case;

public class Simple {

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void assertFalse() {
    assert false;
  }

  public static void assertBoolean(boolean shouldFail) {
    assert shouldFail;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void assertBoolean_true(boolean shouldFail) {
    assertBoolean(true);;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void assertBoolean_false(boolean shouldFail) {
    assertBoolean(false);;
  }

  public static void assertInteger(int n) {
    assert n != 0;
  }
  
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void assertInteger_1(int n) {
    assertInteger(1);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void assertInteger_0(int n) {
    assertInteger(0);
  }

  public static void assertPositive(int num) {
    assert num > 0;
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void assertPositive_1() {
    assertPositive(1);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void assertPositive_n1() {
    assertPositive(-1);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static int divideByZero() {
    return 1 / 0;
  }

  public static int divideByN(int n) {
    return 1 / n;
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void divideByN_0(int n) {
    divideByN(0);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void divideByN_1(int n) {
    divideByN(1);
  }

  public static int divideZeroByZero(int a, int b) {
    return a / b;
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void divideZeroByZero_0_0() {
    divideZeroByZero(0, 0);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void divideZeroByZero_0_1() {
    divideZeroByZero(0, 1);
  }

  public static int multiError(boolean b) {
    assert b;
    return 1 / 0;
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void multiError_false() {
    multiError(false);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void multiError_true() {
    multiError(true);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static int earlyReturn() {
    if (true) {
      return 0;
    }
    assert false;
    return 0;
  }

  public static int checkBeforeDivideByN(int n) {
    assert n != 0;
    return 1 / n;
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void checkBeforeDivideByN_1() {
    checkBeforeDivideByN(1);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void checkBeforeDivideByN_0() {
    checkBeforeDivideByN(0);
  }

  public static int checkBeforeDivideByN2(int n) {
    if (n != 0) {
      return 1 / n;
    }
    assert 10 > n;
    return 0;
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void checkBeforeDivideByN2_0() {
    checkBeforeDivideByN2(0);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void checkBeforeDivideByN2_1() {
    checkBeforeDivideByN2(1);
  }

  public static void checkBeforeAssert(int n) {
    if (n == 0) {
      return;
    }
    assert 1 / n > 0;
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void checkBeforeAssert_n1() {
    checkBeforeAssert(-1);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void checkBeforeAssert_0() {
    checkBeforeAssert(0);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static int justReturn() {
    return 0;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void justReturnNothing() {
    return;
  }

  public static int divideByNMinus10054203(int n) {
    return 1 / (n - 10054203);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void divideByNMinus10054203_0(int n) {
    divideByNMinus10054203(0);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void divideByNMinus10054203_10054203(int n) {
    divideByNMinus10054203(10054203);
  }

}
