import utils.*;

public class Simple {
    public static int sum(int[] arr) {
        int sum = 0;
        for(int i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
        return sum;
    }

    public static int add(int x, int y) {
        return x + y;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void detectArrayBecomesNull() {
        int[] arrayBecomesNull = new int[]{0, 1, 2, 3};
        assert arrayBecomesNull[1] == 1; // will throw a null pointer exception
    }
    
    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void detectArrayStopsBeingNull() {
        int[] arrayGetsValue = null;
        assert arrayGetsValue[1] == 1; // used to throw a null point exception
    }
    
    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void detectArrayBecomesShorter() {
        int[] arrayBecomesShorter = new int[]{0, 1, 2, 3};
        assert arrayBecomesShorter[3] == 3; // will throw a null pointer exception
    }

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void donNotRunAgainAfterValueDoubles() {
        int[] arrayDoublesInValue = new int[]{0, 1, 2, 3};
        assert arrayDoublesInValue[3] >= 3; // still fine
    }

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void donNotRunAgainAfterArrayBecomesLonger() {
        int length = 4;
        int[] arrayBecomesLonger = new int[length];
        arrayBecomesLonger[3] = 100;
        assert arrayBecomesLonger[3] >= 3; // still fine
    }

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void weDontNeedToSumAnArrayThatDoublesInValueAgain() { // sum of array is larger than before
        int[] arrayDoublesInValue = new int[]{0, 1, 2, 3};
        assert sum(arrayDoublesInValue) >= 3;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void weMustSumAnArrayThatChangesInLengthAgain() { // sum of array is larger than before
        int length = 4;
        int[] arrayBecomesLonger = new int[length];
        arrayBecomesLonger[0] = 100;
        assert sum(arrayBecomesLonger) >= 3;
    }

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void elementHasExpression() {
        int[] arrayHasExpression = new int[]{add(3, 4), 1, 2, 3};
        assert arrayHasExpression[0] >= 5;
    }

    @Test(shouldRunSymbolic = false, shouldRunDynamic = true)
    public void elementGetsExpression() {
        int[] arrayHasExpression = new int[]{0, 1, 2, 3};
        assert arrayHasExpression[0] >= 0;
        arrayHasExpression[0] = add(3, 4);
        assert arrayHasExpression[0] >= 5;
    }

    @Test(shouldRunSymbolic = true, shouldRunDynamic = true)
    public void ifTheIndexWeUseForAConditionChangesWeMustRunAgain() { // sum of array is larger than before
        // in the first iteration we update index 0, which is does not change the result
        // but in the next iteration we update the value, which should cause the test to rerun
        // this test is here because the expression will be cache the value stored at index 1, 
        // and this could lead to the test not being rerun
        // We should detect that the test should be rerun because we assign to a different position in the array
        int[] arrayDoesNotChange = new int[]{0, 1, 2, 3};
        int indexBecomeOne = 0;
        arrayDoesNotChange[indexBecomeOne] = 99;
        assert arrayDoesNotChange[1] == 1;
    }

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
