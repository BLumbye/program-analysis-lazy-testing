import utils.*;

public class Simple {

    static final int SOME_CONSTANT = 43;

    static int factorial(int n){      
        if (n == 0) {
            return 1;      
        }
        return(n * factorial(n-1));      
    }      

    @Test(shouldBeRunAgain = false)
    public void unchanged() {
        assert factorial(1000) == 42;
    }

    
    @Test(shouldBeRunAgain = false)
    public void stillWrongAfterLocalChange() {
        assert factorial(1000) == 42;
    }

    @Test(shouldBeRunAgain = false)
    public void stillWrongAfterStaticVariableChange() {
        assert factorial(1000) == SOME_CONSTANT;
    }
    
    @Test(shouldBeRunAgain = true)
    public void mustChange() {
        assert factorial(1000) == 42;
    }
}
