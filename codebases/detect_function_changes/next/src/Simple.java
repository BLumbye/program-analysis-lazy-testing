import utils.*;

public class Simple {

    static final int SOME_CONSTANT = 42;

    public static int B() {
        return SOME_CONSTANT;
    }
    

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void testOnlyChangesInlineConstants() {
        assert B() == 43;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void testChangesImplementation() {
        assert (B() / 2 * 2) == 42;
    }
    
    public static int C() {
        int c = 0;
        for (int i = 0; i < 1; i++) {
            c += SOME_CONSTANT;
        }
        return c;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void testDependencyChangesImplementation() {
        assert C() == 42;
    }
}
