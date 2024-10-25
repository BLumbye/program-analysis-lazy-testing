package utils;
import java.lang.annotation.Annotation;
import java.lang.annotation.Repeatable;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.reflect.Method;



// Make Words annotation repeatable
@Retention(RetentionPolicy.RUNTIME)
public @interface Test {
    boolean shouldBeRunAgain() default false;
}
