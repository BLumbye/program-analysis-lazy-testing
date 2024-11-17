import utils.*;

public class Simple {

    static final int SOME_CONSTANT = 43;

    public static int J(int x) {
        for(int i = 0; i < 11; i++) {
            x++;
        }
        return x;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void simpleTest() {
        assert J(0) == 10;
    }
}
