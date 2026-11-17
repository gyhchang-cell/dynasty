package artifacts.component;

@FunctionalInterface
public interface ComponentAccumulator<ACC, C> {

    ACC accumulate(ACC acc, C element);

}
