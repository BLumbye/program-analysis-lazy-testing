import utils.*;

public class Callee {
    @Test(shouldRunSymbolic = true)
    public void simpleTest() {
        assert Simple.B() == 42;
    }
}
