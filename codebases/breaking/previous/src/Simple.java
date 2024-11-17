import utils.*;

public class Simple {

    @Test(shouldBeRunAgain = true)
    public static void arrayIsNullLength() {
      int array[] = null;
      assert array.length == 0;
    }
}
