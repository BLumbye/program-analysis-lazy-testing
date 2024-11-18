import utils.*;

public class Simple {

    static int SOME_CONSTANT = 5;

    @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
    public void unchanged() {
        assert SOME_CONSTANT == Fields.A + Fields.B;
    }
    
    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void different_result() {
        assert SOME_CONSTANT == Fields.A + Fields.C;
    }
    
    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void stillTrue() {
        assert Fields.A < Fields.C;
    }
}
