import utils.*;

public class Simple {

    static final int SOME_CONSTANT = 43;

    static int factorial(int n){      
        if (n == 0) {
            return 1;      
        }
        return(n * factorial(n-1));      
    }      

    @Test(shouldRunSymbolic = false, shouldRunDynamic = false)
    public void unchanged() {
        assert factorial(100) == 42;
    }

    
    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void stillWrongAfterLocalChange() {
        assert factorial(100) == 42;
    }

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void stillWrongAfterStaticVariableChange() {
        assert factorial(100) == SOME_CONSTANT;
    }
    
    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void mustChange() {
        assert factorial(100) == 42;
    }
}
