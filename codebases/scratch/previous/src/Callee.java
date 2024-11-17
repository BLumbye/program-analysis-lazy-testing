import nested.Simpler;
import utils.*;

public class Callee {
    @Test(shouldRunSymbolic = true)
    public void simpleTest() {
        assert Simpler.constant() == 42;
    }
}
