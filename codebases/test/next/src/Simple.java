import utils.*;

public class Simple {

    @Test(shouldRunDynamic = true, shouldRunSymbolic = true)
    public static void neverAsserts() {
        int i = 1;
        while (i > 0) {
        }
        assert false;
    }
}
