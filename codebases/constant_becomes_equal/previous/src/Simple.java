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

    @Test(shouldBeRunAgain = true)
    public void simpleTest() {
        assert B() == 42;
    }
}
