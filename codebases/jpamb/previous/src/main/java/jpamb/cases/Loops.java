package jpamb.cases;
import utils.*;
import jpamb.utils.*;
import static jpamb.utils.Tag.TagType.*;

public class Loops {

  // @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  // @Tag({ LOOP })
  // public static void forever() {
  //   while (true) {
  //   }
  // }

  // @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  // @Tag({ LOOP })
  // public static void neverAsserts() {
  //   int i = 1;
  //   while (i > 0) {
  //   }
  //   assert false;
  // }

  // @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  // @Tag({ LOOP })
  // public static int neverDivides() {
  //   int i = 1;
  //   while (i > 0) {
  //   }
  //   return 0 / 0;
  // }

  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  @Tag({ LOOP, INTEGER_OVERFLOW })
  public static void terminates() {
    short i = 0;
    while (i++ != 0) {
    }
    assert false;
  }
}
