import utils.*;

public class Simple {

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void cmpArrays() {
        int array1[] = { 1, 2, 100, -13, 23 };
        int array2[] = { 1, 2, 100, -13, 23 };
        assert array1.length == array2.length;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void cmpArrayElems() {
        int array1[] = { 1, 2, 100, -13, 23 };
        int array2[] = { 1, 2, 100, -13, 23 };
        for (int i = 0; i < array1.length; i++) {
          assert array1[i] == array2[i];
        }
    }
}
