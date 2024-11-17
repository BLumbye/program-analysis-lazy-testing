import utils.*;

public class Simple {

    static final int SOME_CONSTANT = 43;

    public static int A() {
        return 5;
    }

    public static int B() {
        A();
        return SOME_CONSTANT;
    }

    public static boolean C1() {
        int x = 1;
        return x > 0 && x < 100;
    }

    public static boolean C2() {
        int x = 0;
        return !(x > 0 && x < 100);
    }

    public static boolean C3() {
        int x = 0;
        return x > 0 && x < 100 || x == 1;
    }

    public static boolean D() {
        int x = 0;
        return !(x > 0 || x < 100);
    }

    public static boolean E() {
        int x = 0;
        return !(x > 0 || !(x < 100));
    }

    public static int F() {
        return -1;
    }

    public static int G() {
        int x = 0;
        return -x;
    }

    public static boolean H() {
        int x = 0;
        return x++ == 0;
    }

    public static boolean I() {
        int x = 0;
        return x-- == 0;
    }

    @Test(shouldRunSymbolic = true)
    public void simpleTest() {
        assert B() == 42;
    }
}
