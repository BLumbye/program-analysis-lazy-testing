import utils.*;

public class Simple {

    static final int SOME_CONSTANT = 42;

    public static int B() {
        return SOME_CONSTANT;
    }

    @Test(shouldBeRunAgain = true)
    public void testOnlyChangesInlineConstants() {
        assert B() == 42;
    }

    @Test(shouldBeRunAgain = false)
    public void testChangesImplementation() {
        assert B() == 42;
    }
    
    public static int C() {
        return SOME_CONSTANT;
    }

    @Test(shouldBeRunAgain = true)
    public void testDependencyChangesImplementation() {
        assert C() == 42;
    }
}
