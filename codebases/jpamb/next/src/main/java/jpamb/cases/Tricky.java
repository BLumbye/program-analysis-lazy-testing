package jpamb.cases;

import utils.*;
import jpamb.utils.*;
import static jpamb.utils.Tag.TagType.*;

public class Tricky {
  @Tag({ LOOP })
  public static void collatz(int n) { 
    assert n > 0;
    while (n != 1) { 
      if (n % 2 == 0) { 
        n = n / 2;
      } else { 
        n = n * 3 + 1;
      }
    }
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void collatz_0(int n) { 
    collatz(0);
  }
  @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
  public static void collatz_24(int n) { 
    collatz(24);
  }

}
