import nested.Simpler;
import utils.*;

public class Callee {
    @Test(shouldBeRunAgain = true)
    public void simpleTest() {
        assert Simpler.constant() == 42;
    }
}
