import utils.*;

public class Simple {

    static final int SOME_CONSTANT = 42;

    public static int B() {
        return SOME_CONSTANT;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void testOnlyChangesInlineConstants() {
        assert B() == 42;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void testChangesImplementation() {
        assert B() == 42;
    }
    
    public static int C() {
        return SOME_CONSTANT;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void testDependencyChangesImplementation() {
        assert C() == 42;
    }
}
