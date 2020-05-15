package devices

type %(className) struct {
	BaseDevice
	bus            []string
	//由表格导入的常数
	%(constListCode)[]float64
	//状态变量(索引)
	%(stateVListCode)   []int
	//代数变量(索引)
	%(algebVListCode) []int

	//内部变量
	%(internalVListCode) []float64
}

func (%(name) * %(className)) Initial(dae *dae.Dae, set *settings.Settings) {
	%(name).BaseDevice.Initial(dae, set)
	%(name).deviceType ="%(className)"
	%(name).stOrder = []string{%(stOrderCode)}
	%(name).alOrder = []string{%(alOrderCode)}

	%(name).pVarS["name"] = &%(name).Name
	%(name).pVarS["bus"] = &%(name).bus

	%(initalCode)

}

func (%(name) * %(className)) Add(f map[string]float64, s map[string]string) {
	%(name).BaseDevice.Add(f, s)
	%(name).state = append(%(name).state, 1)
	%(name).gammaP = append(%(name).gammaP, 1)
	%(name).gammaQ = append(%(name).gammaQ, 1)
	%(addCode)
}


func (%(name) *%(className)) SetX0() {
	for i:=0; i<%(name).N; i++ {

		// 1.根据设备的不同情况进行预处理
		// 2.计算常量
		//代数变量索引
		//运算关系转化
		%(setX0Code)
	}
}


func (%(name) *%(className)) CalG() {
	for i:=0; i<%(name).N; i++ {
		// 1.计算代数方程
		// 2.赋值
		%(calGCode1)

	}
}

func (%(name) *%(className)) CalF() {
	for i:=0; i<%(name).N; i++ {
		//1. 将DAE中的值提取到变量中
		//2. 计算更新状态方程的值
		//3. 更新DAE
		%(calFCode1)

	}
}

func (%(name) *%(className)) CalGy() {
	for i:=0; i<%(name).N; i++ {
		%(calGyCode1)
	}
}

func (%(name) *%(className)) CalFx() {
	for i:=0; i<%(name).N; i++ {
		//1. 将DAE中的值提取到变量中
		%(calFxCode1)

	}
}
//根据实际的母线基准值标幺化
//func (%(name) *%(className)) Base() {
//	for i:=0; i<template.N; i++ {
//		vb := template.pBus.Vb[template.pBus.index[template.bus[i]]]
//		sb := template.pSettings.Mva
//		zb := vb * vb / sb
//
//		//template.xd[i] /= zb
//		//template.xd1[i] /= zb
//		//template.xd2[i] /= zb
//
//	}
//}


//func (%(name) *%(className)) BusIndex() {
//	for _, eachBus := range template.bus {
//		//busNum:母线名称对应的编号
//		busNum := template.pBus.index[eachBus]
//		template.Va = append(template.Va, template.pBus.va[busNum])
//		template.V0 = append(template.V0, template.pBus.v0[busNum])
//	}
//}
//
