import utils.*;

public class Simple {
    public static int sum(int[] arr) {
        int sum = 0;
        for(int i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
        return sum;
    }
    
    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void detectArrayBecomesNull() {
        int[] arrayBecomesNull = null;
        assert arrayBecomesNull[1] == 1; // will throw a null pointer exception
    }
    
    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void detectArrayStopsBeingNull() {
        int[] arrayGetsValue = new int[]{0, 1, 2, 3};
        assert arrayGetsValue[1] == 1; // used to throw a null point exception
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void detectArrayBecomesShorter() {
        int[] arrayBecomesShorter = new int[]{0, 1};
        assert arrayBecomesShorter[3] == 3; // will throw a null pointer exception
    }

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void donNotRunAgainAfterValueDoubles() {
        int[] arrayDoublesInValue = new int[]{0, 2, 4, 6};
        assert arrayDoublesInValue[3] >= 3; // will throw a null pointer exception
    }
    
    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void donNotRunAgainAfterArrayBecomesLonger() {
        int length = 8;
        int[] arrayBecomesLonger = new int[length];
        arrayBecomesLonger[3] = 100;
        assert arrayBecomesLonger[3] >= 3; // still fine
    }

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void weDontNeedToSumAnArrayThatDoublesInValueAgain() { // sum of array is larger than before
        int[] arrayDoublesInValue = new int[]{0, 2, 4, 6};
        assert sum(arrayDoublesInValue) >= 3;
    }
    
    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void weMustSumAnArrayThatChangesInLengthAgain() { // sum of array is larger than before
        int length = 8;
        int[] arrayBecomesLonger = new int[length];
        arrayBecomesLonger[0] = 100;
        assert sum(arrayBecomesLonger) >= 3;
    }
    
    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void ifTheIndexWeUseForAConditionChangesWeMustRunAgain() { // sum of array is larger than before
        // in the first iteration we update index 0, which is does not change the result
        // but in the next iteration we update the value, which should cause the test to rerun
        // this test is here because the expression will be cache the value stored at index 1, 
        // and this could lead to the test not being rerun
        // We should detect that the test should be rerun because we assign to a different position in the array
        int[] arrayDoesNotChange = new int[]{0, 1, 2, 3};
        int indexBecomeOne = 1;
        arrayDoesNotChange[indexBecomeOne] = 99;
        assert arrayDoesNotChange[1] == 1;
    }
}
