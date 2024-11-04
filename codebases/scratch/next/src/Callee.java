import utils.*;

public class Callee {
    @Test(shouldBeRunAgain = true)
    public void simpleTest() {
        assert Simple.B() == 42;
    }
}
