import utils.*;

public class Simple {

    static int SOME_CONSTANT = 5;

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void simpleTest() {
        assert SOME_CONSTANT == Fields.A + Fields.B;
    }
}
