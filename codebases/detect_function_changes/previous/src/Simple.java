import utils.*;

public class Simple {

    static int SOME_CONSTANT = 42;

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
    
    public static int MethodThatChangesImplementation() {
        return SOME_CONSTANT;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void testDependencyChangesImplementation() {
        assert MethodThatChangesImplementation() == 42;
    }
    
    @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
    public void testAFunctionThatCouldHaveBeenCalledChangesImplementation() {
        if (SOME_CONSTANT < 100000) {
            assert SOME_CONSTANT > 0;
        } else {
            assert MethodThatChangesImplementation() == 42; // not run
        }
    }
}
