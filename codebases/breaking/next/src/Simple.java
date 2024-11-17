import utils.Test;

public class Simple {

    @Test(shouldRunDynamic = true, shouldRunSymbolic = true)
    public static void arrayIsNullLength() {
      int array[] = null;
      assert array.length == 0;
    }
}
