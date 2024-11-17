import utils.*;

public class Simple {

    static final int SOME_CONSTANT = 42;

    public static int A() {
        return 8;
    }

    public static int B() {
        A();
        return SOME_CONSTANT;
    }

    public static int C(int a) {
        return a + SOME_CONSTANT;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void simpleTest() {
        assert B() == 42;
    }
}
