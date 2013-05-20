


class Poisson:
    
    def cumulant(self, u, expo):
        la = self.p_lambda.integrated(expo.t0, expo.t1)
        expo.a = la*(exp(u*self.p_jump.value()) - 1.0)
        expo.b[0] = 0