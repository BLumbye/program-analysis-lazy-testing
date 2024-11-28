package jpamb.cases;
import utils.*;
import jpamb.utils.*;
import static jpamb.utils.Tag.TagType.*;

public class Arrays {

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ ARRAY })
  public static void arrayOutOfBounds() {
    int array[] = { 0, 0 };
    array[3] = 0;
  }
  


  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ ARRAY })
  public static void arrayInBounds() {
    int array[] = { 0, 0 };
    array[1] = 1;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ ARRAY })
  public static void arrayLength() {
    int array[] = { 0, 0 };
    assert array.length == 2;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ ARRAY })
  public static void arrayIsNull() {
    int array[] = null;
    array[1] = 10;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ ARRAY })
  public static void arrayIsNullLength() {
    int array[] = null;
    assert array.length == 0;
  }

  @Tag({ ARRAY })
  public static void arraySometimesNull(int i) {
    int array[] = null;
    if (i < 10) {
      array = new int[] { i };
    }
    array[1] = 10;
  }
  
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void arraySometimesNull_0() {
    arraySometimesNull(0);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void arraySometimesNull_11() {
    arraySometimesNull(0);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ ARRAY })
  public static void arrayContent() {
    int array[] = { 1, 2, 100, -13, 23 };
    for (int i = 0; i < array.length; i++) {
      assert i > 0;
    }
  }

  @Tag({ ARRAY })
  public static void binarySearch(int x) {
    int arr[] = { 2, 3, 4, 10, 40 };
    int l = 0, r = arr.length - 1;
    while (l <= r) {
      int m = l + (r - l) / 2;
      if (arr[m] == x)
        return;
      if (arr[m] < x)
        l = m + 1;
      else
        r = m - 1;
    }
    assert false;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ ARRAY })
  public static void binarySearch_3() {
    binarySearch(3);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ ARRAY })
  public static void binarySearch_6() {
    binarySearch(6);
  }

  @Tag({ ARRAY })
  public static void arrayNotEmpty(int[] array) {
    assert array.length > 0;
  }
  
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void arrayNotEmpty_() {
    arrayNotEmpty(new int[0]);
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void arrayNotEmpty_1() {
    arrayNotEmpty(new int[] {1});
  }

  @Tag({ ARRAY })
  public static void arraySpellsHello(char[] array) {
    assert array[0] == 'h'
        && array[1] == 'e'
        && array[2] == 'l'
        && array[3] == 'l'
        && array[4] == 'o';
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void arraySpellsHello_hello() {
    arraySpellsHello(new char[] {'h', 'e', 'l', 'l', 'o'});
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void arraySpellsHello_x() {
    arraySpellsHello(new char[] { 'x' });
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void arraySpellsHello_() {
    arraySpellsHello(new char[] { });
  }

  @Tag({ ARRAY })
  public static void arraySumIsLarge(int[] array) {
    int sum = 0;
    for (int i = 0; i < array.length; i++) {
      sum += array[i];
    }
    assert sum > 300;
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void arraySumIsLarge_50_100_200() {
    arraySumIsLarge(new int[] {50, 100, 200});
  }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void arraySumIsLarge_() {
    arraySumIsLarge(new int[] {});
  }
}
