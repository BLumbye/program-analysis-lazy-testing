package utils;
import java.lang.annotation.Annotation;
import java.lang.annotation.Repeatable;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.reflect.Method;



// Mark tests
@Retention(RetentionPolicy.RUNTIME)
public @interface Test {
    boolean shouldRunSymbolic() default false;
    boolean shouldRunDynamic() default true;
}
